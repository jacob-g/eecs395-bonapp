from flask import abort, request
from libs import objects
from libs.db import DBConnector
from datetime import datetime

type = "page"

status_minutes = 30 #the number of minutes back to look at statuses

def preempt(db : DBConnector, metadata : dict, dining_hall_name : str):
    if objects.DiningHall.from_list(metadata["dining_halls"], dining_hall_name) is None:
        return abort(404)

def page_data(db : DBConnector, metadata : dict, dining_hall_name : str):
    dining_hall : objects.DiningHall = objects.DiningHall.from_list(metadata["dining_halls"], dining_hall_name)
    
    meal : str = dining_hall.next_meal_after(datetime.now().time()) \
                    if "meal" not in request.args or request.args["meal"] not in dining_hall.hours \
                    else request.args["meal"]
        
    time = datetime.today()
    if "date" in request.args:
        try:
            time = datetime.strptime(request.args["date"], "%Y-%m-%d")
        except ValueError:
            None
    
    date = time.date()
            
    return {"dining_hall": dining_hall,
            "meal": meal,
            "date": date,
            "menu": dining_hall.menu(date, meal, db), 
            "inventory": dining_hall.inventory(status_minutes, db)}