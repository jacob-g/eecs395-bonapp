from flask import redirect, abort
from libs import objects

#TODO: put this into a configuration file
status_minutes = 30 #the number of minutes back to look at statuses

type = "action"

def preempt(db, metadata : dict, dining_hall_name : str, item_id : str, *args, **kwargs):
    #TODO: check if the dining hall exists
    if metadata["login_state"].user is None or objects.DiningHall.from_list(metadata["dining_halls"], dining_hall_name) is None or db.inventory_item(item_id) is None:
        return abort(404)
    else:
        return None

def action(db, metadata : dict, dining_hall_name : str, item_id : int, status : int):
    db.add_status(objects.DiningHall.from_list(metadata["dining_halls"], dining_hall_name), db.inventory_item(item_id), status, metadata["login_state"].user, status_minutes)
    return redirect(f"/dining_hall/{dining_hall_name}")