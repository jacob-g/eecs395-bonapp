from libs.db import DBConnector
import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import json



type = "page"

def create_food_plot():

    foods=['carrots', 'potatoes', 'cultural appropriation']

    fig = go.Figure(data=[
        go.Bar(name='Rating Today', x=foods, y=[3, 4, 2]),
        go.Bar(name='Average Rating', x=foods, y=[2.5, 4.5, 2])
    ])
    # Change the bar mode
    fig.update_layout(barmode='group',
                        xaxis_title='Menu Items',
                        yaxis_title='Rating Score')

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def create_amenities_plot():

    timings=['12:00PM','1:00PM','2:00PM','3:00PM','4:00PM']
    forks = ['3','1','2','2.2','1.5']
    knives = ['3','3','2.5','3','3']
    spoons = ['2.5','2','1','1.5','3']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timings, y=forks,
                    mode='lines+markers',
                    name='forks'))
    fig.add_trace(go.Scatter(x=timings, y=knives,
                    mode='lines+markers',
                    name='knives'))
    fig.add_trace(go.Scatter(x=timings, y=spoons,
                    mode='lines+markers',
                    name='spoons'))

    fig.update_layout(xaxis_title="Amentities", yaxis_title="Availability")
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def preempt(db : DBConnector, metadata : dict):
    return None

def page_data(db : DBConnector, metadata : dict):
    return {"food_plot": create_food_plot(), "amenities_plot": create_amenities_plot()}
