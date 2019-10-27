from flask import redirect, request, abort
from libs.db import DBConnector

type = "action"

def preempt(db : DBConnector, metadata : dict):
    serves_id = request.form["serves_id"]
    
    if db.served_item(serves_id) is None or metadata["login_state"].user is None:
        return abort(404)

def action(db : DBConnector, metadata : dict):
    serves_id = request.form["serves_id"]
    
    db.add_review(metadata["login_state"].user, request.form["rating"], request.form["comment"], serves_id)
    
    return redirect(f"/reviews/specific/{serves_id}")