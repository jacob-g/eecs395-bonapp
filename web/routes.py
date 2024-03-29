from flask import Flask, send_from_directory
from libs.db import DBConnector
from libs import loader
from page_behaviors import index, static_page, logout, add_review, delete_review, add_status, dining_hall_page, view_reviews, alerts_page, add_alert, remove_alert, metrics,\
	send_contact

#TODO: put this login into its own file
app = Flask(__name__)
app.secret_key = "abc123"
app.template_folder = "static/templates"
app.static_folder = "static"
app.static_url_path = ""

page_metadata = []

routes = {
	"/": {"template": "main.html", "behavior": index, "methods": ["GET"]},
	"/contact": {"template": "contact.html", "behavior": static_page, "methods": ["GET"]},
	"/logout": {"template": "empty.html", "behavior": logout, "methods": ["GET"]},
	"/actions/leave_review": {"template": "empty.html", "behavior": add_review, "methods": ["POST"]},
	"/actions/delete_review": {"template": "empty.html", "behavior": delete_review, "methods": ["POST"]},
	"/actions/add_status": {"template": "empty.html", "behavior": add_status, "methods": ["POST"]},
	"/actions/send_contact": {"template": "empty.html", "behavior": send_contact, "methods": ["POST"]},
	"/dining_hall/<dining_hall_name>": {"template": "hall.html", "behavior": dining_hall_page, "methods": ["GET"]},
	"/reviews/specific/<serves_id>": {"template": "review.html", "behavior": view_reviews, "methods": ["GET"]},
	"/alerts": {"template": "alerts.html", "behavior": alerts_page, "methods": ["GET"]},
	"/alerts/add": {"template": "empty.html", "behavior": add_alert, "methods": ["POST"]},
	"/alerts/remove/<alert_id>": {"template": "empty.html", "behavior": remove_alert, "methods": ["GET"]},
	"/metrics": {"template": "metrics.html", "behavior": metrics, "methods": ["GET"]}
}

loader_funcs = []

for url, page_spec in routes.items():
	loader_func = lambda page_spec=page_spec, *args, **kwargs: loader.load_page(page_spec["template"], page_spec["behavior"], *args, **kwargs)
	loader_func.__name__ = f"load:{url}"
		
	app.route(url, methods=page_spec["methods"])(loader_func)