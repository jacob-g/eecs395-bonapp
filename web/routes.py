from flask import Flask
from libs.db import DBConnector
from libs import loader
from page_behaviors import index

#TODO: put this login into its own file
app = Flask(__name__)
app.secret_key = "abc123"

dbLink = DBConnector()

page_metadata = []

routes = {
	"/": ("index.html", index)
}

for url, page_spec in routes.items():
	app.route(url)(lambda: loader.load_page(page_spec[0], page_spec[1].page_data, dbLink))