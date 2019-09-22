from flask import Flask
from libs import db
app = Flask(__name__)

@app.route("/")
def index():
	return "test"