from flask import redirect, request, abort
from libs.db import DBConnector

type = "action"

def preempt(db : DBConnector, metadata : dict):    
    if metadata["login_state"].user is None or metadata["login_state"].user.role != "admin":
        return abort(404)

def action(db : DBConnector, metadata : dict):
    review_id = request.form["review_id"]
    
    db.delete_review(review_id)
    
    return redirect(request.referer)