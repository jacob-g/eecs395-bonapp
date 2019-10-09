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
	def dining_halls(self):
		diningHalls = []
		
		row = {}
		for (row["dining_hall.name"], ) in self.__query("SELECT name FROM dining_hall ORDER BY name ASC"):
			diningHalls.append(objects.DiningHall.from_db(row))
			
		return diningHalls
	
	def served_item(self, serves_id):
		result = self.__query("SELECT serves.meal,menu_item.id,menu_item.name,dining_hall.name FROM serves LEFT JOIN menu_item ON menu_item.id=serves.menu_item_id LEFT JOIN dining_hall ON dining_hall.name=serves.dining_hall_name WHERE serves.id=%s ORDER BY menu_item.name ASC", (serves_id,))
		
		row = {}
		if len(result) == 1:
			(row["serves.meal"], row["menu_item.id"], row["menu_item.name"], row["dining_hall.name"]) = result[0]
			return objects.MenuItemServed(serves_id, objects.MenuItem.from_db(row, objects.DiningHall.from_db(row)), row["serves.meal"])
		else:
			return None
			
	def menu_for(self, dining_hall, date = datetime.date.today()):
		menu_items = []
				
		row = {}
		for (row["serves.id"], row["serves.meal"], row["menu_item.id"], row["menu_item.name"]) in self.__query("SELECT serves.id,serves.meal,menu_item.id,menu_item.name FROM serves LEFT JOIN menu_item ON menu_item.id=serves.menu_item_id WHERE serves.dining_hall_name=%s AND serves.date_of=%s ORDER BY menu_item.name ASC", (dining_hall.name, date)):
			menu_items.append(objects.MenuItemServed.from_db(row, dining_hall))
			
		return menu_items
		
	def user_for(self, name):
		res = self.__query("SELECT id, name FROM user WHERE name=%s LIMIT 1", (name))
		if res.len() == 1:
			return objects.User(res[0], res[1])
		else:
			return None
		
	def add_user_if_not_exists(self, user):			
		self.__query("INSERT INTO `user`(id, name) SELECT %s, %s FROM DUAL WHERE (SELECT COUNT(1) FROM user WHERE id=%s)=0", (user.id, user.name, user.id), True)
		return
		
	#TODO: encapsulate all the data with the Review object
	def add_review(self, user, rating, comments, serves_id):
		self.__query("INSERT INTO review(user, rating, comments, item) VALUES(%s, %s, %s, %s)", (user.id, rating, comments, serves_id), True)
		return
	
	def allowed_scores(self):
		scores = []
		
		for row in self.__query("SELECT score FROM allowed_scores ORDER BY score ASC"):
			scores.append(row[0])
			
		return scores
		
	def reviews_for(self, menuItem):
		reviews = []
		
		row = {}
		cursor = self.__query("SELECT review.rating,review.comments,item FROM review LEFT JOIN review_of ON review_of.review_id=review.id WHERE review_of.menu_item_id=%s", (menuItem.id))
		for row["review.rating"], row["review.comments"] in cursor:
			reviews.append(objects.Review.from_db(row, menuItem))
			
		cursor.close()
		return reviews