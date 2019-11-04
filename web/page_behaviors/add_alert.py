from flask import abort, redirect
from libs.db import DBConnector

type = "action"

def preempt(db : DBConnector, metadata : dict, menu_item_id : int):    
    if db.menu_item(menu_item_id) is None or metadata["login_state"].user is None:
        return abort(404)
    
def action(db : DBConnector, metadata : dict, menu_item_id : int):
    db.add_alert(metadata["login_state"].user, menu_item_id)
    
    return redirect(f"/alerts")