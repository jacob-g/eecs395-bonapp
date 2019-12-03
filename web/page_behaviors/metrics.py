from libs.db import DBConnector
from libs import funcs
from datetime import datetime
from flask import abort
import simplejson as json

type = "page"

<<<<<<< HEAD
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
=======
def preempt(db : DBConnector, metadata : dict):
    if metadata["login_state"].user is None or metadata["login_state"].user.role != "admin":
        return abort(404) 
    
    return    
    
def page_data(db : DBConnector, metadata : dict):
    date = funcs.date_from_request()
    
    review_stats = db.average_daily_and_total_ratings(date)
    
    menu_item_names = ["%s (%s, %s)" % (review_stat[0].menu_item.name, review_stat[0].dining_hall.name, review_stat[0].meal) for review_stat in review_stats]
    dailies = [review_stat[0].average_rating for review_stat in review_stats]
    totals = [review_stat[1] for review_stat in review_stats]
        
    return {"date": date, "menu_items": json.dumps(menu_item_names, use_decimal = True), "dailies": json.dumps(dailies, use_decimal = True), "totals": json.dumps(totals, use_decimal = True)}
>>>>>>> d66e2aad6fd3101be29e3c8cce6a8887912bee9b
