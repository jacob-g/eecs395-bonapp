type = "page"

def page_data(db, dining_hall_name):
    dining_hall = [dining_hall for dining_hall in db.dining_halls() if dining_hall.name == dining_hall_name][0]
    #TODO: reject unknown dining halls, return a 404
    return {"dining_hall": dining_hall, "menu": db.menu_for(dining_hall)}