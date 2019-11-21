from flask import abort, redirect
from libs.db import DBConnector

type = "action"

def preempt(db : DBConnector, metadata : dict, alert_id : int):  
    if metadata["login_state"].user is None:
        return abort(404)
    
def action(db : DBConnector, metadata : dict, alert_id : int):
    db.remove_alert(alert_id, metadata["login_state"].user)
    
    return redirect(f"/alerts")