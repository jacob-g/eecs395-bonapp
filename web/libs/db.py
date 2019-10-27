import mysql.connector
import datetime
from libs import objects
from torch.distributions.constraints import boolean
from libs.objects import InventoryItem

class DBConnector:
	host="localhost"
	username="bonapp"
	password="password"
	dbname="review"
	def __init__(self):
		self.link=mysql.connector.connect(host=self.host, user=self.username, password=self.password, database=self.dbname)
		
	def __query(self, query : str, args : tuple =(), makes_changes : boolean = False):
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
	
	def __single_row(self, query : str, args : tuple, constructor):
		result = self.__query(query, args)
		if len(result) == 1:
			return constructor(result[0])
		else:
			return None
		
	#TODO: factor out some of this logic into a lambda function representing a constructor
	def dining_halls(self):
		diningHalls = []
		
		row = {}
		for (row["dining_hall.name"], ) in self.__query("SELECT name FROM dining_hall ORDER BY name ASC"):
			diningHalls.append(objects.DiningHall.from_db(row))
			
		return diningHalls
	
	def served_item(self, serves_id : int):
		result = self.__query("SELECT serves.meal,menu_item.id,menu_item.name,dining_hall.name FROM serves LEFT JOIN menu_item ON menu_item.id=serves.menu_item_id LEFT JOIN dining_hall ON dining_hall.name=serves.dining_hall_name WHERE serves.id=%s ORDER BY menu_item.name ASC", (serves_id,))
		
		row = {}
		if len(result) == 1:
			(row["serves.meal"], row["menu_item.id"], row["menu_item.name"], row["dining_hall.name"]) = result[0]
			return objects.MenuItemServed(serves_id, objects.MenuItem.from_db(row, objects.DiningHall.from_db(row)), row["serves.meal"])
		else:
			return None
			
	#TODO: make this take no date by default
	def menu_for(self, dining_hall : objects.DiningHall, date : datetime.date = datetime.date.today()):
		menu_items = []
				
		row = {}
		for (row["serves.id"], row["serves.meal"], row["menu_item.id"], row["menu_item.name"]) in self.__query("SELECT serves.id,serves.meal,menu_item.id,menu_item.name FROM serves LEFT JOIN menu_item ON menu_item.id=serves.menu_item_id WHERE serves.dining_hall_name=%s AND serves.date_of=%s ORDER BY menu_item.name ASC", (dining_hall.name, date)):
			menu_items.append(objects.MenuItemServed.from_db(row, dining_hall))
		
		print(menu_items)
			
		return menu_items
	
	def all_menu_items(self):
		menu_items = []
		
		row = {}
		for (row["menu_item.id"], row["menu_item.name"]) in self.__query("SELECT menu_item.id,menu_item.name FROM menu_item ORDER BY menu_item.name ASC"):
			menu_items.append(objects.MenuItem.from_db(row))
			
		return menu_items
		
	def user_for(self, user_id : str):
		return self.__single_row("SELECT id, name FROM user WHERE id=%s LIMIT 1", (user_id,), lambda res : objects.User(res[0], res[1]))
		
	def add_user_if_not_exists(self, user : objects.User):			
		self.__query("INSERT INTO `user`(id, name) SELECT %s, %s FROM DUAL WHERE (SELECT COUNT(1) FROM user WHERE id=%s)=0", (user.user_id, user.name, user.user_id), True)
		return
		
	#TODO: encapsulate all the data with the Review object
	def add_review(self, user : objects.User, rating : int, comments : str, serves_id : int):
		self.__query("INSERT INTO review(user, rating, comments, item) VALUES(%s, %s, %s, %s)", (user.user_id, rating, comments, serves_id), True)
		return
	
	def allowed_scores(self):
		scores = []
		
		for (score,) in self.__query("SELECT score FROM allowed_scores ORDER BY score ASC"):
			scores.append(score)
			
		return scores
	
	def inventory_for(self, dining_hall : objects.DiningHall, minutes : int):
		inventories = []
		
		row = {}
		for (row["inventory_item.id"], row["inventory_item.name"], row["status"]) in self.__query("SELECT inventory_item.id,inventory_item.name,AVG(statuses.status) AS status FROM inventory_item LEFT JOIN statuses ON inventory_item.id=statuses.item_id AND statuses.dining_hall=%s AND statuses.time_stamp>(NOW() - INTERVAL %s MINUTE) GROUP BY inventory_item.id", (dining_hall.name, minutes)):
			inventories.append(objects.InventoryStatus(objects.InventoryItem.from_db(row), row["status"]))
		
		return inventories
	
	def inventory_item(self, item_id : int):
		return self.__single_row("SELECT inventory_item.id,inventory_item.name FROM inventory_item WHERE inventory_item.id=%s", (item_id, ), lambda row : objects.InventoryItem(row[0], row[1]))
	
	def add_status(self, dining_hall : objects.DiningHall, inventory_item : objects.InventoryItem, status : int, user : objects.User, minutes : int):
		self.__query("INSERT INTO statuses(item_id,status,dining_hall,time_stamp,user) SELECT %s, %s, %s, NOW(), %s FROM DUAL WHERE (SELECT COUNT(1) FROM statuses WHERE user=%s AND dining_hall=%s AND item_id=%s AND time_stamp>(NOW() - INTERVAL %s MINUTE))=0", (inventory_item.item_id, status, dining_hall.name, user.user_id, user.user_id, dining_hall.name, inventory_item.item_id, minutes), True)
		return
		
	def reviews_for(self, menu_item : objects.MenuItem):
		reviews = []
		
		row = {}
		for (row["review.rating"], row["review.comments"], row["user.id"], row["user.name"]) in self.__query("SELECT review.rating,review.comments,user.id,user.name FROM review LEFT JOIN review_of ON review_of.review_id=review.id LEFT JOIN serves ON serves.id=review.item LEFT JOIN user ON user.id=review.user WHERE serves.menu_item_id=%s", (menu_item.id,)):
			reviews.append(objects.Review.from_db(row, menu_item))
			
		return reviews
	
	def add_alert(self, user_id, menu_item_id):
		self.__query("INSERT INTO alert(user, menu_item_id) VALUES(%s, %s)", (user_id, menu_item_id), True)
		return
	
	def alerts_for(self, user : objects.User):
		alerts = []
		
		row = {}
		for (row["alert.id"], row["menu_item.id"], row["menu_item.name"]) in self.__query("SELECT alert.id,menu_item.id,menu_item.name FROM alert LEFT JOIN menu_item ON menu_item.id=alert.menu_item_id"):
			alerts.append(objects.AlertSubscription.from_db(row, user))
			
		return alerts
	
	def remove_alert(self, alert : objects.AlertSubscription):
		self.__query("DELETE FROM alert WHERE id=%s", (alert.alert_id, ), True)
		return