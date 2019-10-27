from flask import abort
from libs import objects
from libs.db import DBConnector

type = "page"

def preempt(db : DBConnector, metadata : dict):
    if metadata["login_state"].user is None:
        return abort(404)

def page_data(db : DBConnector, metadata : dict):
    return {"alert_subscriptions": db.alerts_for(metadata["login_state"].user), "all_menu_items": db.all_menu_items()}