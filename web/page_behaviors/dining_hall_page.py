from flask import abort, request
from libs import objects
from libs.db import DBConnector
from datetime import datetime
from libs import funcs

type = "page"

status_minutes = 30 #the number of minutes back to look at statuses

def preempt(db : DBConnector, metadata : dict, dining_hall_name : str):
    if objects.DiningHall.from_list(metadata["dining_halls"], dining_hall_name) is None or ("meal" in request.args and request.args["meal"] not in objects.DiningHall.from_list(metadata["dining_halls"], dining_hall_name).hours):
        return abort(404)

def page_data(db : DBConnector, metadata : dict, dining_hall_name : str):
    dining_hall : objects.DiningHall = objects.DiningHall.from_list(metadata["dining_halls"], dining_hall_name)
    
    (meal, date) = dining_hall.next_meal_after(datetime.now().time())
    
    if "meal" in request.args:
        meal = request.args["meal"]
    
    if "date" in request.args:
        date = funcs.date_from_request()
                    
    return {"dining_hall": dining_hall,
            "meal": meal,
            "date": date,
            "menu": dining_hall.menu(date, meal, db),
            "inventory": dining_hall.inventory(status_minutes, db)}