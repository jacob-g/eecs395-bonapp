import mysql.connector
import datetime
from libs import objects

class DBConnector:
	host="localhost"
	username="bonapp"
	password="password"
	dbname="review"
	def __init__(self):
		self.link=mysql.connector.connect(host=self.host, user=self.username, password=self.password, database=self.dbname)
		
	def __query(self, query, args=(), makes_changes=False):
		cursor = self.link.cursor()
		cursor.execute(query, args)
		
		if makes_changes:
			result = None
			self.link.commit()
			cursor.close()
		else:
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
		
	def menu_for(self, dining_hall, date = datetime.date.today()):
		menuItems = []
		
		row = {}
		for (row["menu_item.id"], row["menu_item.name"]) in self.__query("SELECT menu_item.id,menu_item.name FROM serves LEFT JOIN menu_item ON menu_item.id=serves.menu_item_id WHERE serves.dining_hall_name=%s AND serves.date_of=%s ORDER BY menu_item.name ASC", (dining_hall.name, date)):
			menuItems.append(objects.MenuItem.from_db(row, dining_hall))
			
		return menuItems
		
	def user_for(self, name):
		res = self.__query("SELECT id, name FROM user WHERE name=%s LIMIT 1", (name))
		if res.len() == 1:
			return objects.User(res[0], res[1])
		else:
			return None
		
	def add_user_if_not_exists(self, user):			
		self.__query("INSERT INTO `user`(id, name) SELECT %s, %s FROM DUAL WHERE (SELECT COUNT(1) FROM user WHERE id=%s)=0", (user.id, user.name, user.id), True)
		return
		
	def addReview(self, review, user):
		self.__query("INSERT INTO review(user, rating, comments, item) VALUES(%s, %s, %s, %s)", (user.id, review.rating, review.comments, review.item.id), True).close()
		return
		
	def reviewsFor(self, menuItem):
		reviews = []
		
		row = {}
		cursor = self.__query("SELECT review.rating,review.comments,item FROM review LEFT JOIN review_of ON review_of.review_id=review.id WHERE review_of.menu_item_id=%s", (menuItem.id))
		for row["review.rating"], row["review.comments"] in cursor:
			reviews.append(objects.Review.from_db(row, menuItem))
			
		cursor.close()
		return reviews