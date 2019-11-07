from flask import abort
from libs import objects
from libs.db import DBConnector
import datetime

type = "page"

status_minutes = 30 #the number of minutes back to look at statuses

def preempt(db : DBConnector, metadata : dict, dining_hall_name : str):
    if objects.DiningHall.from_list(metadata["dining_halls"], dining_hall_name) is None:
        return abort(404)

def page_data(db : DBConnector, metadata : dict, dining_hall_name : str):
    dining_hall : objects.DiningHall = objects.DiningHall.from_list(metadata["dining_halls"], dining_hall_name)
    meal : str = dining_hall.next_meal_after(datetime.datetime.now().time())
    
    return {"dining_hall": dining_hall,
            "meal": meal,
            "menu": dining_hall.menu(datetime.datetime.today().date(), meal, db), 
            "inventory": dining_hall.inventory(status_minutes, db)}