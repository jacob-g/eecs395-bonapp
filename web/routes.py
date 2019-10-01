from flask import Flask, render_template
from libs.db import DBConnector
from libs import objects

app = Flask(__name__)

dbLink = DBConnector()

@app.route("/")
def index():
	print(dbLink.menuFor(dbLink.diningHalls()[1], "2019-09-25"))
	return "test"
