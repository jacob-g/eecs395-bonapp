from flask import Flask
from libs.db import DBConnector
app = Flask(__name__)

dbLink = DBConnector()

@app.route("/")
def index():
	print(dbLink.diningHalls())
	return "test"