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
		result = cursor.fetchall()
		cursor.close()
		return result
		
	#TODO: factor out some of this logic into a lambda function representing a constructor
	def diningHalls(self):
		diningHalls = []
		
		row = {}
		for db_row in self.__query("SELECT name FROM dining_hall ORDER BY name ASC"):
			row["dining_hall.name"] = db_row[0]
			diningHalls.append(objects.DiningHall.from_db(row))
			
		return diningHalls
		
	def menuFor(self, diningHall, date):
		menuItems = []
		
		row = {}
		for db_row in self.__query("SELECT menu_item.id,menu_item.name FROM serves LEFT JOIN menu_item ON menu_item.id=serves.menu_item_id WHERE date_of=%s AND serves.dining_hall_name=%s ORDER BY menu_item.name ASC", (date, diningHall.name)):
			row["menu_item.id"] = db_row[0]
			row["menu_item.name"] = db_row[1]
			menuItems.append(objects.MenuItem.from_db(row))
			
		return menuItems
		
	def userFor(self, name):
		res = self.__query("SELECT id, name FROM user WHERE name=%s LIMIT 1", (name))
		if res.len() == 1:
			return objects.User(res[0], res[1])
		else:
			return None
		
	def addReview(self, review):
		self.__query("INSERT INTO review(user, rating, comments, item) VALUES(%s, %s, %s, %s)", ("jvg11", review.rating, review.comments, review.item.id)).close()
		return
		
	def reviewsFor(self, menuItem):
		reviews = []
		
		row = {}
		cursor = self.__query("SELECT review.rating,review.comments,item FROM review LEFT JOIN review_of ON review_of.review_id=review.id WHERE review_of.menu_item_id=%s", (menuItem.id))
		for row["review.rating"], row["review.comments"] in cursor:
			reviews.append(objects.Review.from_db(row, menuItem))
			
		cursor.close()
		return reviews