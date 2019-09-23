from MySQLdb import _mysql

class DBConnector:
	host="localhost"
	username="bonapp"
	password="password123"
	dbname="bonapp"
	def __init__(self):
		self.link=db=_mysql.connect(host, username, password, dbname)
		
	def __query(self, query):
		self.link.query(query)
		return self.link.use_result()