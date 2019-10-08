from flask import Flask
from libs.db import DBConnector
from libs import loader
from page_behaviors import index, logout, add_review, leave_review, dining_hall_page

#TODO: put this login into its own file
app = Flask(__name__)
app.secret_key = "abc123"

dbLink = DBConnector()

page_metadata = []

routes = {
	"/": {"template": "index.html", "behavior": index, "methods": ["GET"]},
	"/logout": {"template": "empty.html", "behavior": logout, "methods": ["GET"]},
	"/actions/leave_review": {"template": "empty.html", "behavior": add_review, "methods": ["POST"]},
	"/dining_hall/<dining_hall_name>": {"template": "dining_hall.html", "behavior": dining_hall_page, "methods": ["GET"]},
	"/leave_review/<menu_item_id>": {"template": "leave_review.html", "behavior": leave_review, "methods": ["GET"]}
}

loader_funcs = []

for url, page_spec in routes.items():
	loader_func = lambda page_spec=page_spec, *args, **kwargs: loader.load_page(page_spec["template"], page_spec["behavior"], dbLink, *args, **kwargs)
	loader_func.__name__ = f"load:{url}"
		
	app.route(url, methods=page_spec["methods"])(loader_func)
	