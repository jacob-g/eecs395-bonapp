from libs import login
from flask import redirect

type = "action"

def action(db):
	login.LoginState.logout_user()
	return redirect("/")