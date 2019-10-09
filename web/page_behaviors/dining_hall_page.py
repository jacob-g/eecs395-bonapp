from flask import abort

type = "page"

def get_dining_hall(metadata, dining_hall_name):
    dining_hall_candidates = [dining_hall for dining_hall in metadata["dining_halls"] if dining_hall.name == dining_hall_name]
    if len(dining_hall_candidates) == 0:
        return None
    else:
        return dining_hall_candidates[0]

def preempt(db, metadata, dining_hall_name):
    if get_dining_hall(metadata, dining_hall_name) is None:
        return abort(404)

def page_data(db, metadata, dining_hall_name):
    dining_hall = get_dining_hall(metadata, dining_hall_name)
    return {"dining_hall": dining_hall, "menu": db.menu_for(dining_hall)}