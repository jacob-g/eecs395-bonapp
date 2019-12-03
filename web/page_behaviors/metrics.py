from libs.db import DBConnector
from libs import funcs, objects
from datetime import datetime
from flask import abort, request
import simplejson as json

type = "page"

def hourly_availibility_from_list(availabilities : list, dining_hall : objects.DiningHall, hour : int):
    hourly_availibilities = [status[1].status for status in availabilities if status[1].dining_hall.name == dining_hall.name and status[0] == hour]
    return 0 if len(hourly_availibilities) == 0 else hourly_availibilities[0]

def preempt(db : DBConnector, metadata : dict):
    if metadata["login_state"].user is None or metadata["login_state"].user.role != "admin" or ("inventory" in request.args and db.inventory_item(request.args["inventory"]) is None):
        return abort(404)

    return

def page_data(db : DBConnector, metadata : dict):
    date = funcs.date_from_request()

    review_stats = db.average_daily_and_total_ratings(date)

    menu_item_names = ["%s (%s, %s)" % (review_stat[0].menu_item.name, review_stat[0].dining_hall.name, review_stat[0].meal) for review_stat in review_stats]
    dailies = [review_stat[0].average_rating for review_stat in review_stats]
    totals = [review_stat[1] for review_stat in review_stats]

    data = {"date": date, 
            "menu_items": json.dumps(menu_item_names, use_decimal = True),
            "daily_food_ratings": json.dumps(dailies, use_decimal = True), 
            "historical_food_ratings": json.dumps(totals, use_decimal = True),
            "all_inventory_items": db.all_inventory_items()}

    if "inventory" in request.args:
        data["hours"] =  list(range(24))

        inventory_item = db.inventory_item(request.args["inventory"])
        
        historical_availibilities = db.average_inventory_availibility_by_hour(inventory_item)
        daily_availibilities = db.daily_inventory_availibility_by_hour(inventory_item, date)
        
        data["historical_availabilities"] = {}
        data["daily_availabilities"] = {}

        for dining_hall in db.dining_halls():
            data["historical_availabilities"][dining_hall] = [hourly_availibility_from_list(historical_availibilities, dining_hall, hour) for hour in range(0, 24)]
            data["daily_availabilities"][dining_hall] = [hourly_availibility_from_list(daily_availibilities, dining_hall, hour) for hour in range(0, 24)]
                        
    return data