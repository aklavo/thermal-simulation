#!/usr/bin/env python3
import json
import sys
from dash import Dash, html, dcc , Input, Output
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


app = Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])

# App components
# case_id_dropdown = dcc.Dropdown(id='case-id',options=case_id_dic,value=most_recent_case_id, clearable=False)
# date_picker_range = dcc.DatePickerRange(id='date-picker', disabled=True, updatemode='bothdates')
# power_radio = dcc.RadioItems(id='power',options=['Facility', 'HVAC'], value= 'HVAC',inputStyle={"margin-right": "3px"},labelStyle={"margin-right": "10px"})
# model_checklist = dcc.Checklist(id='comp-model',options=['OPT','NSU', 'DEF'], value=['OPT','DEF'],inputStyle={"margin-right": "3px"},labelStyle={"margin-right": "10px"})
# setpoint_dropdown = dcc.Dropdown(id='setpoint',options=setpoint_list,value=setpoint_list[0], clearable=False)
# floor_dropdown = dcc.Dropdown(id='temperature',options=temp_list,value='SecondFloorZone5', clearable=False)
# PDR_output = html.Div(id='PDR',style={'font-size':16})
# HVAC_PDR_output = html.Div(id='HVAC-PDR',style={'font-size':16}) 

graph = dcc.Graph(id='graph',config={'responsive':True},figure={'layout':{'height':700}})

app.layout = dbc.Container([
    html.H1('Solar Panel - Thermal Simulation'),
    dbc.Row([
    ]),
    dbc.Row([
        graph
    ],justify="center")
],fluid=True)

# @app.callback(
#     Input()
# )
# def update():

#     return None



if __name__ == '__main__':
    app.run_server(debug=True)#host="0.0.0.0", port="8050")
