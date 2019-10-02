import cas
from libs import objects

class LoginState:
	def __init__(self, ticket=None):
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
			self.user=objects.User(verState[1]["user"], verState[1]["displayName"])
		
		else:
			self.user = None