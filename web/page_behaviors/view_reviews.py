from flask import abort
from libs.db import DBConnector

type = "page"

def preempt(db : DBConnector, metadata : dict, serves_id : int):
    if db.served_item(serves_id) is None:
        return abort(404)

def page_data(db : DBConnector, metadata : dict, serves_id : int):
    served_item = db.served_item(serves_id)
    return {"served_item": served_item, "reviews": db.reviews_for(served_item.menu_item)}