# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import os
from dash.dependencies import Input, Output
import plotly_express as px
import pandas as pd
import datetime as dt
import numpy as np
from sklearn import linear_model
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from sqlalchemy import create_engine
import sql_key
import csv
import matplotlib.pyplot as plt 
import random
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
import fun
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.externals import joblib



# sql connection
engine = create_engine(sql_key.key, echo=False)

# current script path
script_path = os.path.dirname(os.path.realpath(__file__))

################################################################################
## find common user_id to see what we can predict
# see individual user progression data
# predict progression speed
query = 'select * from user_ALSFRS_score'
df_ASL_progression = pd.read_sql(query, con=engine)
# convert to datetime
df_ASL_progression['report_date'] = pd.to_datetime(df_ASL_progression['report_date'], format='%Y-%m-%d')
df_ASL_progression['report_date'] = df_ASL_progression['report_date'].map(dt.datetime.toordinal)
# unique user_id
unique_user_id = df_ASL_progression['user_id'].unique()

# user_condition data
# select only the user id in ASL_progression data
query = 'select * from user_condition'
df_user_conditions = pd.read_sql(query, con=engine)
# find unique id and conditions
# unique user_id
unique_user_id_2 = df_user_conditions['user_id'].unique()
# unique conditions
unique_conditon = df_user_conditions['condition_name'].unique()

# user_symptom data
query = 'select * from user_symptom'
df_user_symptoms = pd.read_sql(query, con=engine)
# find unique id and conditions
# unique user_id
unique_user_id_3 = df_user_symptoms['user_id'].unique()
# unique conditions
unique_symptom = df_user_symptoms['symptom_name'].unique()

# see individual user onset date
query = 'select * from user_onset_date'
df_user_onset_date = pd.read_sql(query, con=engine)
# convert to datetime
df_user_onset_date['first_definitive_diagnosis_date'] = pd.to_datetime(df_user_onset_date['first_definitive_diagnosis_date'], format='%Y-%m-%d')
df_user_onset_date['first_definitive_diagnosis_date'] = df_user_onset_date['first_definitive_diagnosis_date'].map(dt.datetime.toordinal)
# unique user_id
unique_user_id_4 = df_user_onset_date['user_id'].unique()

# condition map 
CONDITION_MAP = {}
for i in range(len(unique_conditon)):
    CONDITION_MAP[unique_conditon[i]] = i

# symptom map 
# use only top 500 symptoms
SYMPTOM_MAP = {}
n = 300
top_n_symptom = df_user_symptoms['symptom_name'].value_counts()[:n].index.tolist()
for i in range(len(top_n_symptom)):
    SYMPTOM_MAP[top_n_symptom[i]] = i

################################################################################
## predict progression rate based on condition
# only use common user presented in user_progression, user_condition, and user onset_data
# split now, 90% for training, 10% from testing
training_user_id = np.load(script_path + '/training_testing_ids/training_progression_user_id.npy')
testing_user_id = np.load(script_path + '/training_testing_ids/testing_progression_user_id.npy')

# based on user progression calcualte progression speed
# that is the one we want to predict
progression_speed = []
for user_id in training_user_id:
    #print(user_id)
    user_progression = df_ASL_progression[df_ASL_progression['user_id'] == user_id]
    m = fun.getProgressionspeed(user_progression)
    progression_speed.append(m)

# build predictors that is the condtions each user have
have_conditions = []
for user_id in training_user_id:
    user_conditions = df_user_conditions[df_user_conditions['user_id'] == user_id]
    user_conditions_code = fun.getConditions(CONDITION_MAP, user_conditions)
    have_conditions.append(user_conditions_code)

# linear model to predict progression rate
X = np.asarray(have_conditions)
y = np.asarray(progression_speed)

reg = LinearRegression().fit(X, y)
reg.score(X, y)


# Save to file in the current working directory
model_file = script_path + '/trained_models/progression_model.pkl'
joblib.dump(reg, model_file)

# Load from file
reg = joblib.load(model_file)

# run test on test user_id
progression_speed_test = []
for user_id in testing_user_id:
    #print(user_id)
    user_progression = df_ASL_progression[df_ASL_progression['user_id'] == user_id]
    m = fun.getProgressionspeed(user_progression)
    progression_speed_test.append(m)

have_conditions_test= []
for user_id in testing_user_id:
    user_conditions = df_user_conditions[df_user_conditions['user_id'] == user_id]
    user_conditions_code = fun.getConditions(CONDITION_MAP, user_conditions)
    have_conditions_test.append(user_conditions_code)

progression_speed_predicted = reg.predict(have_conditions_test)

plt.plot(progression_speed_test, '-o')
plt.plot(progression_speed_predicted, '-o')
plt.show()


###############################################################################
## predict condition based on reported symptoms
# user condition symptom pair
# find common user id between user_condition and user_symptom
training_user_id_cs  = np.load(script_path + '/training_testing_ids/training_condition_symptom_user_id.npy')
testing_user_id_cs = np.load(script_path + '/training_testing_ids/testing_condition_symptom_user_id.npy')

# based on user progression calcualte progression speed
# that is the one we want to predict
all_user_conditions = []
all_user_symptoms = []
for user_id in training_user_id_cs:
    # load corresponding condition
    user_conditions = df_user_conditions[df_user_conditions['user_id'] == user_id]
    # we only consider user with one condtion for now
    if len(user_conditions) > 1:
        continue
    # load corresponding symptom
    user_symptoms = df_user_symptoms[df_user_symptoms['user_id'] == user_id]
    
    # build condition label
    condition_label = fun.getConditionlabel(CONDITION_MAP, user_conditions)
    all_user_conditions.append(condition_label)
    
    # buid symtoms code to predict label
    user_symtoms_code = fun.getSymptomcode(SYMPTOM_MAP, user_symptoms)
    all_user_symptoms.append(user_symtoms_code)


# try a desicion tree
X = np.asarray(all_user_symptoms)
y = np.asarray(all_user_conditions)
bdt = AdaBoostClassifier(DecisionTreeClassifier(max_depth=175),
                         algorithm="SAMME",
                         n_estimators=250)
bdt.fit(X, y)

# test
all_user_conditions_test = []
all_user_symptoms_test = []
for user_id in testing_user_id_cs:
    # load corresponding condition
    user_conditions = df_user_conditions[df_user_conditions['user_id'] == user_id]
    # we only consider user with one condtion for now
    if len(user_conditions) > 1:
        continue
    # load corresponding symptom
    user_symptoms = df_user_symptoms[df_user_symptoms['user_id'] == user_id]
    
    # build condition label
    condition_label = fun.getConditionlabel(CONDITION_MAP, user_conditions)
    all_user_conditions_test.append(condition_label)
    
    # buid symtoms code to predict label
    user_symtoms_code = fun.getSymptomcode(SYMPTOM_MAP, user_symptoms)
    all_user_symptoms_test.append(user_symtoms_code)

test_score = bdt.score(all_user_symptoms_test, all_user_conditions_test)
