from MySQLdb import _mysql
from libs import objects

class DBConnector:
	host="localhost"
	username="bonapp"
	password="password"
	dbname="review"
	def __init__(self):
		self.link=_mysql.connect(self.host, self.username, self.password, self.dbname)
		
	#TODO: make this resistant to SQL injection!!!
	def __query(self, query, args=()):
		self.link.query(query % args)
		print(query % args)
		return self.link.store_result().fetch_row(maxrows=0)
	
	def __decode(self, bin):
		return bin.decode("utf-8")
		
	def diningHalls(self):
		diningHalls = []
		for row in self.__query("SELECT name FROM dining_hall ORDER BY name ASC"):
			diningHalls.append(objects.DiningHall(self.__decode(row[0])))
		return diningHalls
		
	def menuFor(self, diningHall, date):
		menuItems = []
		for row in self.__query("SELECT menu_item.name FROM serves LEFT JOIN menu_item ON menu_item.id=serves.menu_item_id WHERE date_of='%s' AND serves.dining_hall_name='%s' ORDER BY menu_item.name ASC", (date, diningHall.name)):
			menuItems.append(objects.MenuItem(self.__decode(row[0])))
		return menuItems