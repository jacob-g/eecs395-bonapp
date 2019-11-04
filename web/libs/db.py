import mysql.connector
import datetime
from libs import objects
from libs.objects import InventoryItem

class DBConnector:
	host="localhost"
	username="bonapp"
	password="password"
	dbname="review"
	def __init__(self):
		self.link=mysql.connector.connect(host=self.host, user=self.username, password=self.password, database=self.dbname)
		
	def __query(self, query : str, args : tuple =(), makes_changes : bool = False):
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
		
	def __multiple_rows(self, query : str, params : dict, args, constructor):
		output = []
		
		for result in self.__query(query.format(params = ",".join(params.keys())), args):
			assert len(result) == len(params)
			
			row = {}
			index : int = 0
			for dictionary_key in params.values():
				row[dictionary_key] = result[index]
				index = index + 1
				
			output.append(constructor(row))
			
		return output
	
#	def __multiple_rows_provisional(self, query : str, params : dict, args, constructor):
#		return self.__multiple_rows(query % ",".join(params.keys()), args, tuple(params.values()), constructor)
		
	def dining_halls(self):
		return self.__multiple_rows("SELECT {params} FROM dining_hall ORDER BY name ASC",
											 {"name": "dining_hall.name"},
											 (),
											 lambda row : objects.DiningHall.from_db(row))
	
	def served_item(self, serves_id : int):
		result = self.__query("SELECT serves.id,serves.meal,menu_item.id,menu_item.name,dining_hall.name,AVG(review.rating) FROM serves LEFT JOIN menu_item ON menu_item.id=serves.menu_item_id LEFT JOIN review ON review.item=serves.id LEFT JOIN dining_hall ON dining_hall.name=serves.dining_hall_name WHERE serves.id=%s ORDER BY menu_item.name ASC", (serves_id,))
		
		row = {}
		if len(result) == 1:
			(row["serves.id"], row["serves.meal"], row["menu_item.id"], row["menu_item.name"], row["dining_hall.name"], row["average_rating"]) = result[0]
			return objects.MenuItemServed.from_db(row, objects.DiningHall.from_db(row))
		else:
			return None
			
	#TODO: make this take no date by default
	def menu_for(self, dining_hall : objects.DiningHall, date : datetime.date = datetime.date.today()):
		return self.__multiple_rows("SELECT {params} FROM serves LEFT JOIN menu_item ON menu_item.id=serves.menu_item_id LEFT JOIN review ON review.item=serves.id WHERE serves.dining_hall_name=%s AND serves.date_of=%s GROUP BY serves.id ORDER BY menu_item.name ASC",
								{"serves.id": "serves.id", "serves.meal": "serves.meal", "menu_item.id": "menu_item.id", "menu_item.name": "menu_item.name", "AVG(review.rating)": "average_rating"},
								 (dining_hall.name, date),
								 lambda row : objects.MenuItemServed.from_db(row, dining_hall))
	
	def all_menu_items(self):
		return self.__multiple_rows("SELECT {params} FROM menu_item ORDER BY menu_item.name ASC",
								{"menu_item.id": "menu_item.id", "menu_item.name": "menu_item.name"}, 
								(),
								lambda row : objects.MenuItem.from_db(row))
	
	def menu_item(self, menu_item_id):
		return self.__single_row("SELECT menu_item.name FROM menu_item WHERE id=%s", (menu_item_id,), lambda res : objects.MenuItem(id, res[0]))
		
	def user_for(self, user_id : str):
		return self.__single_row("SELECT id, name FROM user WHERE id=%s LIMIT 1", (user_id,), lambda res : objects.User(res[0], res[1]))
		
	def add_user_if_not_exists(self, user : objects.User):			
		self.__query("INSERT INTO `user`(id, name) SELECT %s, %s FROM DUAL WHERE (SELECT COUNT(1) FROM user WHERE id=%s)=0", (user.user_id, user.name, user.user_id), True)
		return
		
	def add_review(self, user : objects.User, rating : int, comments : str, serves_id : int):
		self.__query("INSERT INTO review(user, rating, comments, item) VALUES(%s, %s, %s, %s)", (user.user_id, rating, comments, serves_id), True)
		return
	
	def allowed_scores(self):
		return self.__multiple_rows("SELECT {params} FROM allowed_scores ORDER BY score ASC", 
								{"score": "score"}, 
								(), 
								lambda row : row["score"])
	
	def inventory_for(self, dining_hall : objects.DiningHall, minutes : int):
		return self.__multiple_rows("SELECT {params} FROM inventory_item LEFT JOIN statuses ON inventory_item.id=statuses.item_id AND statuses.dining_hall=%s AND statuses.time_stamp>(NOW() - INTERVAL %s MINUTE) GROUP BY inventory_item.id",
								{"inventory_item.id": "inventory_item.id", "inventory_item.name": "inventory_item.name", "AVG(statuses.status)": "statuses.status"},
								 (dining_hall.name, minutes),
								 lambda row : objects.InventoryStatus.from_db(row, dining_hall))
	
	def inventory_item(self, item_id : int):
		return self.__single_row("SELECT inventory_item.id,inventory_item.name FROM inventory_item WHERE inventory_item.id=%s", (item_id, ), lambda row : objects.InventoryItem(row[0], row[1]))
	
	def add_status(self, dining_hall : objects.DiningHall, inventory_item : objects.InventoryItem, status : int, user : objects.User, minutes : int):
		self.__query("INSERT INTO statuses(item_id,status,dining_hall,time_stamp,user) SELECT %s, %s, %s, NOW(), %s FROM DUAL WHERE (SELECT COUNT(1) FROM statuses WHERE user=%s AND dining_hall=%s AND item_id=%s AND time_stamp>(NOW() - INTERVAL %s MINUTE))=0", (inventory_item.item_id, status, dining_hall.name, user.user_id, user.user_id, dining_hall.name, inventory_item.item_id, minutes), True)
		return
		
	def reviews_for(self, served_menu_item : objects.MenuItemServed):
		return self.__multiple_rows("SELECT {params} FROM review LEFT JOIN review_of ON review_of.review_id=review.id LEFT JOIN serves ON serves.id=review.item LEFT JOIN user ON user.id=review.user WHERE serves.menu_item_id=%s",
								{"review.rating": "review.rating", "review.comments": "review.comments", "user.id": "user.id", "user.name": "user.name"}, 
								(served_menu_item.menu_item.menu_item_id,), 
								lambda row : objects.Review.from_db(row, served_menu_item))
	
	def add_alert(self, user : objects.User, menu_item_id):
		self.__query("INSERT INTO alert(user, menu_item_id) SELECT %s, %s FROM DUAL WHERE (SELECT COUNT(1) FROM alert WHERE user=%s AND menu_item_id=%s)=0", (user.user_id, menu_item_id, user.user_id, menu_item_id), True)
		return
	
	def alerts_for(self, user : objects.User):
		return self.__multiple_rows("SELECT {params} FROM alert LEFT JOIN menu_item ON menu_item.id=alert.menu_item_id WHERE alert.user=%s",
								{"alert.id": "alert.id", "menu_item.id": "menu_item.id", "menu_item.name": "menu_item.name"},
								(user.user_id, ),
								lambda row : objects.AlertSubscription.from_db(row, user))
	
	def remove_alert(self, alert_id : objects.AlertSubscription, user : objects.User):
		self.__query("DELETE FROM alert WHERE id=%s AND user=%s", (alert_id, user.user_id), True)
		return