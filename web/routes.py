from flask import Flask, render_template, request
from libs.db import DBConnector
from libs import objects, login, loader

#TODO: put this login into its own file
app = Flask(__name__)
app.secret_key = "abc123"

dbLink = DBConnector()

routes = {
	"/": "index.html"
}

for url, template in routes.items():
	app.route(url)(lambda: loader.load_page(template, dbLink))