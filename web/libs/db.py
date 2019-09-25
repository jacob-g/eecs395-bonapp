from MySQLdb import _mysql
from libs import objects

class DBConnector:
	host="localhost"
	username="bonapp"
	password="password"
	dbname="review"
	def __init__(self):
		self.link=_mysql.connect(self.host, self.username, self.password, self.dbname)
		
	def __query(self, query):
		self.link.query(query)
		return self.link.store_result().fetch_row(maxrows=0)
		
	def diningHalls(self):
		diningHalls = []
		for row in self.__query("SELECT name FROM dining_hall"):
			diningHalls.append(objects.DiningHall(row[0]))
		return diningHalls