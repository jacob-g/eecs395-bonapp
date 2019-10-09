type = "page"

def page_data(db, serves_id):
    served_item = db.served_item(serves_id)
    return {"served_item": served_item, "reviews": db.reviews_for(served_item.menu_item)}