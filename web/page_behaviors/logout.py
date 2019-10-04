from libs import login

def page_data():
	login.LoginState.logout_user()
	return ""