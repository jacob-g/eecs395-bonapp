from libs.db import DBConnector
from datetime import datetime
from flask import abort
import simplejson as json

type = "page"

def preempt(db : DBConnector, metadata : dict):
    if metadata["login_state"].user is None or metadata["login_state"].user.role != "admin":
        return abort(404) 
    return    
    
def page_data(db : DBConnector, metadata : dict):
    review_stats = db.average_daily_and_total_ratings(datetime.today())
    
    menu_item_names = ["%s (%s, %s)" % (review_stat[0].menu_item.name, review_stat[0].dining_hall.name, review_stat[0].meal) for review_stat in review_stats]
    dailies = [review_stat[0].average_rating for review_stat in review_stats]
    totals = [review_stat[1] for review_stat in review_stats]
        
    return {"menu_items": json.dumps(menu_item_names, use_decimal = True), "dailies": json.dumps(dailies, use_decimal = True), "totals": json.dumps(totals, use_decimal = True)}