type = "page"

def page_data(db, serves_id):
    #TODO: get the menu item ID and the reviews
    return {"served_item": db.served_item(serves_id)}