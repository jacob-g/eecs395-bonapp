from flask import Flask, render_template
from libs.db import DBConnector
from libs import objects

app = Flask(__name__)

dbLink = DBConnector()

@app.route("/")
def index():
	return render_template("index.html")
