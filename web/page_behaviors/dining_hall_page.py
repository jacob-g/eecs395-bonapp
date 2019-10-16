from flask import abort
from libs import objects

type = "page"

status_minutes = 30 #the number of minutes back to look at statuses

def preempt(db, metadata, dining_hall_name):
    if objects.DiningHall.from_list(metadata["dining_halls"], dining_hall_name) is None:
        return abort(404)

def page_data(db, metadata, dining_hall_name):
    dining_hall = objects.DiningHall.from_list(metadata["dining_halls"], dining_hall_name)
    return {"dining_hall": dining_hall, "menu": db.menu_for(dining_hall), "inventory": dining_hall.inventory(status_minutes, db)}