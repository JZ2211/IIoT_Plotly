# Plotly Dash example
# For local deployment at localhost:8050
# The data series are displayed based on the checklist
#
# Created July 2023
# Modified March 2024
# by Jin Zhu
#
# required additional packages: dash, plotly, pandas, firebase_admin
# To install:   pip install dash
#               pip install plotly
#               pip install pandas
#               pip install firebase_admin
#

from datetime import datetime
from dash import Dash, html, dcc, callback, Output, Input 
import plotly.express as px 
import pandas as pd   
import plotly.graph_objects as go   
from plotly.subplots import make_subplots
import math
import firebase_admin
from firebase_admin import credentials
from firebase_retrieve import firebase_retrieve4datetime
from json2csv import convert_json2csv

####################### Modify the following configuration as needed  ##########################################

#Modify the credientail json file name and the database URL for your firebase project
cred=credentials.Certificate('iiot-demo-firebase.json')
firebase_admin.initialize_app(cred, {'databaseURL':'https://iiot-demo-default-rtdb.firebaseio.com'})

#You can export json file for the sensor data on firebase directly 
JSON_FILE = 'example-export.json'  # the json file downloaded from firebase that you want to plot
CSV_FILE = 'nodeMCU.csv'  #choose the csv file name. You may put log_yyyy_mm_dd.txt file here if you want to plot from a locally saved file directly.

#or you may call the function to retrieve data for a specific date
RTDB_PATH = 'test/NodeMCU_A'  #specify the path where the sensor node data stores
START_TIME = '2024-03-21 15:10:00' #specify the start and end date & time if you want to retrieve data for specific during
END_TIME = '2024-03-21 16:45:00'
#comment the next line if you don't need to retrieve the josn file
firebase_retrieve4datetime(RTDB_PATH, START_TIME, END_TIME, JSON_FILE)

#Convert a json file to a csv file for Ploty to use.
#If the data is from a Raspberry pi node, set isNodeMCU = False
#if the data is from a nodeMCU node, set isNodeMCU = True
#comment the next line if you don't need to convert a file to a csv file.
convert_json2csv(JSON_FILE, CSV_FILE, isNodeMCU = True)
dt_NUM =1 #1 by default if the csv file is converted from a json file
#if you want to display plots from a log_yyyy_mm_dd.txt file, change to dt_NUM = 2 

######################### No change is needed below this line ####################################

xdf = pd.read_csv(CSV_FILE) #read dataframe from the csv file
dataseries = list(xdf.columns)  #obtain the list of column names
datetime = dataseries[:dt_NUM] #the first two columns are 'date' & 'time' in log_yyyy_mm_dd.txt files, otherwise the 1st column is timestamp

app = Dash(__name__)        #initialize the app

app.layout = html.Div([
    html.H1(children='Sensor Monitoring Dashboard', style={'textAlign':'center'}),
    html.Div(children=[
        html.Label('Select the data series:'),
        dcc.Checklist(  #generatage a checkist
            id="checklist",
            options = dataseries[dt_NUM:],  #sensor data starts from the 2nd or 3rd column
            value=[dataseries[dt_NUM]], #default checked list with the first item checked
            inline=True,  #compact display in the the same line
            ),
        ]),
    dcc.Graph(id="graph-content"),
])

@callback(   #callback function: return the figure based on the checklist value
    Output(component_id='graph-content', component_property='figure'),
    Input(component_id='checklist', component_property='value')
)
def update_plots(value):
    xdf = pd.read_csv(CSV_FILE) #read dataframe from the csv file
    dataseries = list(xdf.columns)  #obtain the list of column names
    datetime = dataseries[:dt_NUM] #the first two columns are 'date' & 'time' in log_yyyy_mm_dd.txt files, otherwise the 1st column is timestamp
    dt_series=datetime+value # a list of date, time, and checked colums
    df=xdf[dt_series]  #obtain the subset of original data frame based on checklist
    cols =df.columns  #the first two columns are 'Date' and ' Time', and rest are sensor data and we will plot each column as a subplot
                       #the first column is timestamp if it is from nodeMCU

    n_rows = df.shape[0]
    n_cols = df.shape[1]
    empty =" "
    rows = math.ceil(((n_cols-dt_NUM)/2))

    #get the correct headers
    subplot_titles=[]
    for col in range(dt_NUM,n_cols):
        subplot_titles.append(cols[col])

    #get the correct number of rows
    specs = []
    for row in range(rows):
        specs.append([{"type": "scatter"},{"type": "scatter"}])

    #make figure
    fig = make_subplots(
        rows=math.ceil(((n_cols-dt_NUM)/2)), cols=2,
        shared_xaxes=True,
        vertical_spacing = 0.1,
        subplot_titles=subplot_titles,
        specs = specs)

    for col in range(dt_NUM,n_cols):
        if dt_NUM >= 2: #from Raspberry Pi
            fig.add_trace(go.Scatter(x=df[cols[dt_NUM-1]],y=df[cols[col]],mode="lines",name=cols[col]),row=math.floor(col/2), col=(col%2)+1)
            fig.update_yaxes(title_text=cols[col], row=math.floor(col/2), col=math.ceil(col%2)+1)
        else:    #from nodeMCU
            fig.add_trace(go.Scatter(x=df[cols[dt_NUM-1]],y=df[cols[col]],mode="lines",name=cols[col]),row=math.ceil(col/2), col=(col+1)%2+1)
            fig.update_yaxes(title_text=cols[col], row=math.ceil(col/2), col=(col+1)%2+1)
            

    fig.update_xaxes(title_text = cols[dt_NUM-1], row=rows)
    fig.update_layout(
        height=800,
        showlegend=False,
        title_text = "Sensor Monitoring Data from: " + CSV_FILE
        )
    return fig


if __name__ == '__main__':
    app.run(debug=True)   #you the turn debug off by set: debug = False
