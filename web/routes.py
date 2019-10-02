from flask import Flask, render_template
from libs.db import DBConnector
from libs import objects

app = Flask(__name__)

dbLink = DBConnector()

dining_halls = dbLink.diningHalls()

@app.route("/")
def index():
	return render_template("index.html", dining_halls=dining_halls, user=objects.User("jvg11", "Jacob Goldberg"))
