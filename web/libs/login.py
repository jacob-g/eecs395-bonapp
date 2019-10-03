import cas
from libs import objects
from flask import session

class LoginState:
	def __init__(self, ticket=None, Cookie=None):
		self.client = cas.CASClientV3(
                        renew=False,
                        extra_login_params=False,
                        server_url='https://login.case.edu/cas/',
                        service_url='http://localhost:5000/'
                    )
		
		self.login_url = self.client.get_login_url()
		self.logout_url = self.client.get_logout_url("http://localhost:5000")
		
		
		
		#TODO: store the login state in the database and a session
		if ticket is not None:
			verState = self.client.verify_ticket(ticket)
			if verState[0] is not None:
				self.user=objects.User(verState[1]["user"], verState[1]["displayName"])
				session["user"] = self.user.to_dictionary()
		
		elif "user" in session:
			self.user = objects.User.from_dictionary(session.get("user"))
		
		else:
			self.user = None