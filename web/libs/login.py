import cas
from libs import objects
from flask import session

USER_SESSION_KEY = "user"

class LoginState:
	def __init__(self, ticket=None):
		self.client = cas.CASClientV3(
                        renew=False,
                        extra_login_params=False,
                        server_url='https://login.case.edu/cas/',
                        service_url='http://localhost:5000/'
                        
                    )
		
		self.login_url = self.client.get_login_url()
		self.logout_url = self.client.get_logout_url("http://localhost:5000/logout")
		
		if ticket is not None:
			verState = self.client.verify_ticket(ticket)
			if verState[0] is not None:
				self.user=objects.User(verState[1]["user"], verState[1]["displayName"])
				session[USER_SESSION_KEY] = self.user.to_dictionary()
		
		elif USER_SESSION_KEY in session and session.get(USER_SESSION_KEY) is not None:
			self.user = objects.User.from_dictionary(session.get(USER_SESSION_KEY))
		
		else:
			self.user = None
				
	@staticmethod	
	def logout_user():
		session.pop(USER_SESSION_KEY)