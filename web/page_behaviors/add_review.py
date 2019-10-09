from flask import redirect, request
from libs import objects

type = "action"

def action(db, metadata):
    serves_id = request.form["serves_id"]
    
    db.add_review(metadata["login_state"].user, request.form["score"], request.form["comments"], serves_id)
    
    return redirect(f"/reviews/specific/{serves_id}")