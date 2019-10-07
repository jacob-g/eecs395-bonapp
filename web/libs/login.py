import cas
from libs import objects
from flask import session, request, url_for

USER_SESSION_KEY = "user"

class LoginState:
	def __init__(self, ticket=None):
		self.client = cas.CASClientV3(
                        renew=False,
                        extra_login_params=False,
                        server_url='https://login.case.edu/cas/',
                        service_url=request.url_root
                    )
		
		self.login_url = self.client.get_login_url()
		self.logout_url = self.client.get_logout_url(f"{request.url_root}logout")
		
		#there is a user logged in
		if USER_SESSION_KEY in session and session.get(USER_SESSION_KEY) is not None:
			self.user = objects.User.from_dictionary(session.get(USER_SESSION_KEY))
		
		#we got a ticket from CAS, so the user just logged in
		elif ticket is not None:
			verState = self.client.verify_ticket(ticket)
			if verState[0] is not None:
				self.user=objects.User(verState[1]["user"], verState[1]["displayName"])
				session[USER_SESSION_KEY] = self.user.to_dictionary()
		
		#no logged in user
		else:
			self.user = None
				
	@staticmethod	
	def logout_user():
		if USER_SESSION_KEY in session:
			session.pop(USER_SESSION_KEY)