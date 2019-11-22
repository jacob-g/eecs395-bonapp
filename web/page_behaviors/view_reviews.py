from flask import abort, request
from libs.db import DBConnector

type = "page"

def preempt(db : DBConnector, metadata : dict, serves_id : int):
    if db.served_item(serves_id) is None:
        return abort(404)

def page_data(db : DBConnector, metadata : dict, serves_id : int):
    served_item = db.served_item(serves_id)
    
    assert served_item is not None
    
    page = int(request.args["page"]) if "page" in request.args and str.isdigit(request.args["page"]) and int(request.args["page"]) > 0 else 1
    
    return {"served_item": served_item, "reviews": db.reviews_for(served_item, page), "page": page}