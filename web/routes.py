from flask import Flask
from libs.db import DBConnector
from libs import loader
from page_behaviors import index, logout

#TODO: put this login into its own file
app = Flask(__name__)
app.secret_key = "abc123"

dbLink = DBConnector()

page_metadata = []

routes = {
	"/": ("index.html", index)
	#"/logout": ("empty.html", logout)
}

loader_funcs = []

for url, page_spec in routes.items():
	#TODO: make the variables stored inside the lambda
	loader_func = lambda: loader.load_page(page_spec[0], page_spec[1].page_data, dbLink)
	loader_func.__name__ = f"load:{url}"
		
	app.route(url)(loader_func)