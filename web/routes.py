from flask import Flask, render_template, request
from libs.db import DBConnector
from libs import objects, login

app = Flask(__name__)

dbLink = DBConnector()

#load the dining halls from the database
dining_halls = dbLink.diningHalls()

@app.route("/")
def index():
	login_state = login.LoginState(request.args.get("ticket"))
	return render_template("index.html", dining_halls=dining_halls, login_state=login_state)
