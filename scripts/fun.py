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


# function to get user progression speed
def getProgressionspeed(user_progression):
    user_progression_sorted = user_progression.sort_values(by='report_date')
    # try linear fit first
    datetime = user_progression_sorted['report_date'].to_numpy()
    score = user_progression_sorted['score'].to_numpy()
    m, b = np.polyfit(datetime, score, 1)
    return m

# function to get user conditions
def getConditions(CONDITION_MAP, user_conditions):
    user_conditions_code = [0] * len(CONDITION_MAP)
    for condition in user_conditions['condition_name']:
        index = CONDITION_MAP[condition]
        user_conditions_code[index] = 1
    return user_conditions_code
    
# build condition label (int code for condition)
def getConditionlabel(CONDITION_MAP, user_conditions):
    for condition in user_conditions['condition_name']:
        return CONDITION_MAP[condition]
    
# buid symtoms code (predictors for condition)
def getSymptomcode (SYMPTOM_MAP, user_symptoms):
    user_symptoms_code = [0] * len(SYMPTOM_MAP)
    for index, row in user_symptoms.iterrows():
        if row['symptom_name'] in SYMPTOM_MAP:
            symptom_index = SYMPTOM_MAP[row['symptom_name']]
            if row['symptom_severity_score'] == "can't tell temperature":
                user_symptoms_code[symptom_index] = 1
            else:
                user_symptoms_code[symptom_index] = int(row['symptom_severity_score'])
        else:
            continue
    return user_symptoms_code
