from libs import login
from flask import redirect, abort

type = "action"

def preempt(db, metadata):
	if metadata["login_state"].user is None:
		return abort(404)

def action(db, metadata):
	login.LoginState.logout_user()
	return redirect("/")