from libs import login
from flask import redirect

type = "action"

def action():
	login.LoginState.logout_user()
	return redirect("/")