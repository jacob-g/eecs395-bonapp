from libs import login
from flask import redirect

def page_data():
	login.LoginState.logout_user()
	return ""