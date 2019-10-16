from flask import Flask
from libs.db import DBConnector
from libs import loader
from page_behaviors import index, logout, add_review, dining_hall_page, view_reviews, add_status

#TODO: put this login into its own file
app = Flask(__name__)
app.secret_key = "abc123"

dbLink = DBConnector()

page_metadata = []

routes = {
	"/": {"template": "index.html", "behavior": index, "methods": ["GET"]},
	"/logout": {"template": "empty.html", "behavior": logout, "methods": ["GET"]},
	"/actions/leave_review": {"template": "empty.html", "behavior": add_review, "methods": ["POST"]},
	"/actions/status/add/<dining_hall_name>/<item_id>/<status>": {"template": "empty.html", "behavior": add_status, "methods": ["GET"]},
	"/dining_hall/<dining_hall_name>": {"template": "dining_hall.html", "behavior": dining_hall_page, "methods": ["GET"]},
	"/reviews/specific/<serves_id>": {"template": "reviews.html", "behavior": view_reviews, "methods": ["GET"]}
}

loader_funcs = []

for url, page_spec in routes.items():
	loader_func = lambda page_spec=page_spec, *args, **kwargs: loader.load_page(page_spec["template"], page_spec["behavior"], dbLink, *args, **kwargs)
	loader_func.__name__ = f"load:{url}"
		
	app.route(url, methods=page_spec["methods"])(loader_func)
	