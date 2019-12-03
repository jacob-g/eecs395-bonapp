from flask import abort, request
from libs.db import DBConnector
from math import ceil

type = "page"

def get_page():
    return int(request.args["page"]) if "page" in request.args and str.isdigit(request.args["page"]) and int(request.args["page"]) > 0 else 1

def page_of(list, page, page_size = 20):
    assert page > 0
    assert page_size > 0
    
    offset : int = (page - 1) * page_size
    
    return page_size, list[offset:(offset+page_size)] if len(list) > offset else []

def preempt(db : DBConnector, metadata : dict, serves_id : int):
    served_item = db.served_item(serves_id)
    
    if served_item is None:
        return abort(404)
    
    if get_page() > 1 and len(page_of(db.reviews_for(served_item), get_page())[1]) == 0:
        return abort(404)

def page_data(db : DBConnector, metadata : dict, serves_id : int):
    served_item = db.served_item(serves_id)
    
    assert served_item is not None
        
    reviews = db.reviews_for(served_item)
    page_size, paginated_reviews = page_of(reviews, get_page())

    return {"served_item": served_item, "reviews": paginated_reviews, "total_num_pages": ceil(len(reviews) / page_size), "page": get_page()}
