from libs import login
from flask import redirect, abort
from libs.db import DBConnector

type = "action"

def preempt(db : DBConnector, metadata : dict):
	if metadata["login_state"].user is None:
		return abort(404)

def action(db : DBConnector, metadata : dict):
	login.LoginState.logout_user()
	return redirect("/")