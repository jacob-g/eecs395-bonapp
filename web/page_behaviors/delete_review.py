from flask import redirect, request, abort
from libs.db import DBConnector

type = "action"

def preempt(db : DBConnector, metadata : dict):    
    review_id = request.form["review_id"]
    
    if metadata["login_state"].user is None or metadata["login_state"].user.role != "admin" or not db.exists_review_with_id(review_id):
        return abort(404)
    
    return None

def action(db : DBConnector, metadata : dict):
    review_id = request.form["review_id"]
    
    db.delete_review(review_id)
    
    return redirect(request.referer)