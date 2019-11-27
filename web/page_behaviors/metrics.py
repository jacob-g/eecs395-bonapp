from libs.db import DBConnector
import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import json



type = "page"

def create_plot():


    N = 40
    x = np.linspace(0, 1, N)
    y = np.random.randn(N)
    df = pd.DataFrame({'x': x, 'y': y}) # creating a sample dataframe


    data = [
        go.Bar(
            x=df['x'], # assign x as the dataframe column 'x'
            y=df['y']
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def preempt(db : DBConnector, metadata : dict):    
    return None
    
def page_data(db : DBConnector, metadata : dict):
    return {"plot": create_plot()}