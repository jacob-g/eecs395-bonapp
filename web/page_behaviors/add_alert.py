from flask import abort, redirect, request
from libs.db import DBConnector

type = "action"

def preempt(db : DBConnector, metadata : dict):    
    if db.menu_item(request.form["food"]) is None or db.menu_item(request.form["food"]) is None or metadata["login_state"].user is None:
        return abort(404)
    
def action(db : DBConnector, metadata : dict):
    db.add_alert(metadata["login_state"].user, request.form["food"])
    
    return redirect(f"/alerts")