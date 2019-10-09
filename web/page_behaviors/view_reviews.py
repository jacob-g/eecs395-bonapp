from flask import abort

type = "page"

def preempt(db, metadata, serves_id):
    if db.served_item(serves_id) is None:
        return abort(404)

def page_data(db, metadata, serves_id):
    served_item = db.served_item(serves_id)
    return {"served_item": served_item, "reviews": db.reviews_for(served_item.menu_item)}