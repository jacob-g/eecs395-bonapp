from flask import redirect, request, abort

type = "action"

def preempt(db, metadata):
    serves_id = request.form["serves_id"]
    
    if db.served_item(serves_id) is None or metadata["login_state"].user is None:
        return abort(404)

def action(db, metadata):
    serves_id = request.form["serves_id"]
    
    db.add_review(metadata["login_state"].user, request.form["score"], request.form["comments"], serves_id)
    
    return redirect(f"/reviews/specific/{serves_id}")