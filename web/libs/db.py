import mysql.connector
from libs import objects

class DBConnector:
	host="localhost"
	username="bonapp"
	password="password"
	dbname="review"
	def __init__(self):
		self.link=mysql.connector.connect(host=self.host, user=self.username, password=self.password, database=self.dbname)
		
	def __query(self, query, args=()):
		cursor = self.link.cursor()
		cursor.execute(query, args)
		return cursor
		
	#TODO: factor out some of this logic into a lambda function representing a constructor
	def diningHalls(self):
		diningHalls = []
		
		row = {}
		cursor = self.__query("SELECT name FROM dining_hall ORDER BY name ASC")
		for row["dining_hall.name"] in cursor:
			diningHalls.append(objects.DiningHall.from_db(row))
			
		cursor.close()
		return diningHalls
		
	def menuFor(self, diningHall, date):
		menuItems = []
		
		row = {}
		cursor = self.__query("SELECT menu_item.id,menu_item.name FROM serves LEFT JOIN menu_item ON menu_item.id=serves.menu_item_id WHERE date_of=%s AND serves.dining_hall_name=%s ORDER BY menu_item.name ASC", (date, diningHall.name))
		for row["menu_item.id"], row["menu_item.name"] in cursor:
			menuItems.append(objects.MenuItem.from_db(row))
			
		cursor.close()
		return menuItems
		
	def userFor(self, name):
		res = self.__query("SELECT id, name FROM user WHERE name=%s LIMIT 1", (name))
		if res.len() == 1:
			return objects.User(res[0], res[1])
		else:
			return None
		
	def addReview(self, review):
		self.__query("INSERT INTO review()").close()
		return
		
	def reviewsFor(self, menuItem):
		reviews = []
		
		row = {}
		cursor = self.__query("SELECT review.rating,review.comments,item FROM review LEFT JOIN review_of ON review_of.review_id=review.id WHERE review_of.menu_item_id=%s", (menuItem.id))
		for row["review.rating"], row["review.comments"] in cursor:
			reviews.append(objects.Review.from_db(row, menuItem))
			
		cursor.close()
		return reviews