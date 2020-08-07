# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import os
from dash.dependencies import Input, Output
import plotly_express as px
from plotly.subplots import make_subplots
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
import pickle

# current script path
script_path = os.path.dirname(os.path.realpath(__file__))

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

# load testing user ids
# progression speed testing user ids
testing_user_id = np.load(script_path + '/training_testing_ids/testing_progression_user_id.npy')
# condition testing user ids
testing_user_id_cs = np.load(script_path + '/training_testing_ids/testing_condition_symptom_user_id.npy')

# load trained model
# regression model to predict progression speed
model_file = script_path + '/trained_models/progression_model.sav'
reg_progression= pickle.load(open(model_file, 'rb'))
# dt model to predict condition
model_file = script_path + '/trained_models/condition_model.sav'
bdt_condition = pickle.load(open(model_file, 'rb'))

# load constant
# condition map
constant_file = script_path + '/CONDITION_MAP.sav'
CONDITION_MAP = pickle.load(open(constant_file, 'rb'))
# symptom map
constant_file = script_path + '/SYMPTOM_MAP.sav'
SYMPTOM_MAP = pickle.load(open(constant_file, 'rb'))

################################################################################
## app loadout, 2 predictions:
## 1: predict progression speed based on condition
## 2: predict condition based on symptoms
app.layout = html.Div([
    html.Div([html.H4('Predict progression speed based on condition'),
             dcc.Dropdown(id='user_id_progression',
                          options=[{'label': i, 'value': i} for i in testing_user_id],
                          value = 2050),
             dcc.Graph(id='progression_condition')]),
    
    html.Div([html.H4('Predict condition based on symptoms'),
             dcc.Dropdown(id='user_id_condition',
                          options=[{'label': i, 'value': i} for i in testing_user_id_cs],
                          value = 1215),
             dcc.Graph(id='condition_symptom')]) 
])


#predict progression speed based on condition
@app.callback(Output('progression_condition', 'figure'),
              [Input('user_id_progression', 'value')])         
def update_graph(user_id):
    # select from condition table
    # progression data
    query = 'select * from user_ALSFRS_score where user_id = ' + str(user_id)
    user_progression = pd.read_sql(query, con=engine)
    user_progression['report_date'] = pd.to_datetime(user_progression['report_date'], format='%Y-%m-%d')
    user_progression['report_date'] = user_progression['report_date'].map(dt.datetime.toordinal)
    user_progression = user_progression.sort_values(by='report_date')
    time = user_progression['report_date'].to_numpy()
    score = user_progression['score'].to_numpy()
    # condition data
    query = 'select * from user_condition where user_id = ' + str(user_id)
    user_conditions = pd.read_sql(query, con=engine)
    # generate user condition code to predict progression speed 
    # and get true user progression speed
    user_conditions_code = np.asarray(fun.getConditions(CONDITION_MAP, user_conditions))
    # pedict progression speed
    progression_speed_predicted = reg_progression.predict(user_conditions_code.reshape(1, -1))
    predicted_score = progression_speed_predicted[0][0] * time + progression_speed_predicted[0][1]
    # shift up or down based on subject initial score
    predicted_score = predicted_score - (predicted_score[0] - score[0])
    df_predicted = pd.DataFrame({'report_date':time, 'score': predicted_score})
    # begin plot
    #true_m, true_b = np.polyfit(time, score, 1)
    user_progression['report_date'] = user_progression['report_date'].map(dt.datetime.fromordinal)
    df_predicted['report_date'] = df_predicted['report_date'].map(dt.datetime.fromordinal)
    figure = px.scatter(user_progression, x="report_date", y="score", trendline="ols")
    figure.update_traces(name='Actural user data', showlegend = True)
    figure2 = px.line(df_predicted, x = 'report_date', y = 'score')
    figure2.update_traces(name='Predicted progression', showlegend = True)
    figure2.update_traces(line_color='#147852')
    figure.add_trace(figure2.data[0])
    return figure


# predict condition based on symptoms        
@app.callback(dash.dependencies.Output("condition_symptom", 'figure'),
             [dash.dependencies.Input("user_id_condition", "value")])
def update_trace(user_id):
    # get user symptom data
    query = 'select * from user_symptom where user_id = ' + str(user_id)
    user_symptoms = pd.read_sql(query, con=engine)
    user_symtoms_code = np.asarray(fun.getSymptomcode(SYMPTOM_MAP, user_symptoms))
    # get user condition data
    query = 'select * from user_condition where user_id = ' + str(user_id)
    user_condition = pd.read_sql(query, con=engine)
    # predict user_condition based on symptom
    condition_predicted = bdt_condition.predict(user_symtoms_code.reshape(1, -1))
    condition_predicted_name = fun.getConditionname(CONDITION_MAP, condition_predicted)
    # build df to plot
    # real conditions
    user_condition['for_plot'] = [1] * len(user_condition)
    # predicred conditions
    prediced_condition = pd.DataFrame()
    prediced_condition['condition_name'] = [condition_predicted_name]
    prediced_condition['for_plot'] = [1]
    
    
    figure = make_subplots(rows=1, cols=3, 
                           subplot_titles=('User Symptoms',  'Actuall User Conditions', 'Predicted User Conditions'))
    # symptom plot
    figure_1 = px.bar(user_symptoms, x='symptom_name', y='symptom_severity_score', 
                             color='symptom_name')
    for i in range(len(user_symptoms)):
        figure.add_trace (figure_1.data[i], row = 1, col = 1)
    # actuall condition plot
    figure_2 = px.bar(user_condition, x='condition_name', y='for_plot', 
                             color='condition_name')
    for i in range(len(user_condition)):
        figure.add_trace (figure_2.data[i], row = 1, col = 2)
    # predicted condtion plot
    figure_3 = px.bar(prediced_condition, x='condition_name', y='for_plot', 
                             color='condition_name')
    figure.add_trace (figure_3.data[0], row = 1, col = 3)
    
    return figure


if __name__ == '__main__':
    app.run_server(host='0.0.0.0')