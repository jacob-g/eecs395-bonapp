import cas
from libs import objects
from flask import session, request
from libs.db import DBConnector

USER_SESSION_KEY = "user"

class LoginState:
	def __init__(self, db : DBConnector, ticket : str =None):
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
			self.__login_from_session()
		
		#we got a ticket from CAS, so the user just logged in
		elif ticket is not None:
			self.__login_from_cas_ticket(db, ticket)
		
		#no logged in user
		else:
			self.user = None
			
	def __login_from_cas_ticket(self, db : DBConnector, ticket : str):
		verState = self.client.verify_ticket(ticket)
		
		#if the login is valid, then use what CAS gave us to determine the current user and store it
		if verState[0] is not None:
			db_user = db.user_for(verState[1]["user"])
			if db_user is None:
				self.user = objects.User(verState[1]["user"], verState[1]["displayName"])
				self.user.add_to_db(db)
			else:
				self.user = db_user

			 #since this could be the first time the user logs in, add an entry to them in the database if there isn't already one
			session[USER_SESSION_KEY] = self.user.to_dictionary()
			
		return
	
	def __login_from_session(self):
		self.user = objects.User.from_dictionary(session.get(USER_SESSION_KEY))
		return
				
	@staticmethod	
	def logout_user():
		if USER_SESSION_KEY in session:
			session.pop(USER_SESSION_KEY)