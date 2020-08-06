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
  

# create app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# setmapbox style
# current script path
scripty_path = os.path.dirname(os.path.realpath(__file__))
mapbox_access_token = 'pk.eyJ1IjoibXo4NiIsImEiOiJja2J0azVhN3MwOXJhMnpud2VsYjI5ZjJrIn0.8cBcxThR38B2bTaxQ8qsUw'
px.set_mapbox_access_token(mapbox_access_token)

# sql connection
engine = create_engine(sql_key.key, echo=False)

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
df_user_symptom = pd.read_sql(query, con=engine)
# find unique id and conditions
# unique user_id
unique_user_id_3 = df_user_symptom['user_id'].unique()
# unique conditions
unique_symptom = df_user_symptom['symptom_name'].unique()

# see individual user onset date
query = 'select * from user_onset_date'
df_user_onset_date = pd.read_sql(query, con=engine)
# convert to datetime
df_user_onset_date['first_definitive_diagnosis_date'] = pd.to_datetime(df_user_onset_date['first_definitive_diagnosis_date'], format='%Y-%m-%d')
df_user_onset_date['first_definitive_diagnosis_date'] = df_user_onset_date['first_definitive_diagnosis_date'].map(dt.datetime.toordinal)
# unique user_id
unique_user_id_4 = df_user_onset_date['user_id'].unique()

# only use common user presented in user_progression, user_condition, and user onset_data
# split now, 90% for training, 10% from testing
common_user_id = np.intersect1d(unique_user_id, unique_user_id_2)
common_user_id = np.intersect1d(common_user_id, unique_user_id_4)
training_index = random.sample(range(len(common_user_id)), 158)
training_user_id = common_user_id[training_index]
testing_user_id = np.delete(common_user_id, training_index)

























# to do   
# store all user progression slop as the traininng objective
# split the data set to 90% and 10%
# train model on the 90% data (logistic regression, deiciion tree?)
# aggregate to form training data set
# see individual user progression data


















# # select time serails for unique user ID
# for user_id in unique_user_id_1:
#     user_progression = df_ASL_progression[df_ASL_progression.user_id == user_id]
#     user_progression_sorted = user_progression.sort_values(by='report_date')
#     
#     # try linear fit first
#     datetime = user_progression_sorted['report_date'].to_numpy()
#     score = user_progression_sorted['score'].to_numpy()
#     
#     m, b = np.polyfit(datetime, score, 1)
#     plt.plot(datetime, score, 'o')
#     plt.plot(datetime, m*datetime + b)
#     plt.show()
#     print(user_id)
#     print(m)






# if __name__ == '__main__':
#     app.run_server(host='0.0.0.0')
