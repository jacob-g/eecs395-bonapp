import mysql.connector
import datetime
from libs import objects
import json
import os
import sys

def get_root_path():
	return str(os.path.abspath(os.path.dirname(getattr(sys.modules['__main__'], '__file__'))))

class DBConnector:
	def __init__(self):
		with open(os.path.join(get_root_path(), "conf", "dbconf.json")) as json_file:
			db_json = json.load(json_file)
			self.link=mysql.connector.connect(host=db_json["host"], user=db_json["username"], password=db_json["password"], database=db_json["dbname"])

	def _query(self, query : str, args : tuple =(), makes_changes : bool = False):
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
	
	def _row_to_dict(self, result : tuple, keys : tuple):
		assert len(result) == len(keys)
		
		row = {}
		index : int = 0
		for dictionary_key in keys:
			row[dictionary_key] = result[index]
			index = index + 1
			
		return row

	def __single_row(self, query : str, params : dict, args : tuple, constructor):
		results = self.__multiple_rows(query, params, args, constructor)
		return results[0] if len(results) == 1 else None

	def __multiple_rows(self, query : str, params : dict, args : tuple, constructor):
		output = []

		for result in self._query(query.format(params = ",".join(params.keys())), args):
			output.append(constructor(self._row_to_dict(result, params.values())))

		return output
	
	def close(self):
		self.link.close()
		return

	def dining_halls(self):
		return self.__multiple_rows("SELECT {params} FROM dining_hall ORDER BY name ASC",
											 {"name": "dining_hall.name", "breakfast": "dining_hall.meal.breakfast", "lunch": "dining_hall.meal.lunch", "dinner": "dining_hall.meal.dinner", "brunch": "dining_hall.meal.brunch"},
											 (),
											 lambda row : objects.DiningHall.from_db(row))

	def served_item(self, serves_id : int):
		result = self._query("SELECT serves.id,serves.meal,menu_item.id,menu_item.name,dining_hall.name,AVG(review.rating) FROM serves INNER JOIN menu_item ON menu_item.id=serves.menu_item_id LEFT JOIN review ON review.item=serves.id LEFT JOIN dining_hall ON dining_hall.name=serves.dining_hall_name WHERE serves.id=%s ORDER BY menu_item.name ASC", (serves_id,))

		if len(result) == 1 and result[0][0] is not None:
			row = {}
			(row["serves.id"], row["serves.meal"], row["menu_item.id"], row["menu_item.name"], row["dining_hall.name"], row["average_rating"]) = result[0]
			return objects.MenuItemServed.from_db(row, objects.DiningHall.from_db(row))
		else:
			return None

	def menu_for(self, dining_hall : objects.DiningHall, date : datetime.date, meal : str):
		return self.__multiple_rows("SELECT {params} FROM serves LEFT JOIN menu_item ON menu_item.id=serves.menu_item_id LEFT JOIN review ON review.item=serves.id WHERE serves.dining_hall_name=%s AND serves.date_of=%s AND serves.meal=%s GROUP BY serves.id ORDER BY menu_item.name ASC",
								{"serves.id": "serves.id", "serves.meal": "serves.meal", "menu_item.id": "menu_item.id", "menu_item.name": "menu_item.name", "AVG(review.rating)": "average_rating"},
								 (dining_hall.name, date, meal),
								 lambda row : objects.MenuItemServed.from_db(row, dining_hall))

	def all_menu_items(self, pattern="%"):
		return self.__multiple_rows("SELECT {params} FROM menu_item WHERE menu_item.name LIKE %s ORDER BY menu_item.name ASC",
								{"menu_item.id": "menu_item.id", "menu_item.name": "menu_item.name"},
								(pattern, ),
								lambda row : objects.MenuItem.from_db(row))

	def menu_item(self, menu_item_id):
		return self.__single_row("SELECT {params} FROM menu_item WHERE id=%s", 
								{"menu_item.id": "menu_item.id", "menu_item.name": "menu_item.name"}, 
								(menu_item_id,),
								lambda row : objects.MenuItem.from_db(row))

	def user_for(self, user_id : str):
		return self.__single_row("SELECT {params} FROM user WHERE id=%s LIMIT 1",
								{"id": "user.id", "name": "user.name", "role": "user.role"},
								(user_id,),
								lambda row : objects.User.from_db(row))

	def add_user_if_not_exists(self, user : objects.User):
		self._query("INSERT INTO `user`(id, name) SELECT %s, %s FROM DUAL WHERE (SELECT COUNT(1) FROM user WHERE id=%s)=0", (user.user_id, user.name, user.user_id), True)
		return

	def add_review(self, user : objects.User, rating : int, comments : str, serves_id : int):
		self._query("INSERT INTO review(user, rating, comments, item) VALUES(%s, %s, %s, %s)", (user.user_id, rating, comments, serves_id), True)
		return
	
	def delete_review(self, review_id: int):
		self._query("DELETE FROM review WHERE id=%s", (review_id, ), True)
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
		return self.__single_row("SELECT {params} FROM inventory_item WHERE inventory_item.id=%s", 
								{"inventory_item.id": "inventory_item.id", "inventory_item.name": "inventory_item.name"},
								(item_id, ), 
								lambda row : objects.InventoryItem.from_db(row))

	def add_status(self, dining_hall : objects.DiningHall, inventory_item : objects.InventoryItem, status : int, user : objects.User, minutes : int):
		self._query("INSERT INTO statuses(item_id,status,dining_hall,time_stamp,user) SELECT %s, %s, %s, NOW(), %s FROM DUAL WHERE (SELECT COUNT(1) FROM statuses WHERE user=%s AND dining_hall=%s AND item_id=%s AND time_stamp>(NOW() - INTERVAL %s MINUTE))=0", (inventory_item.item_id, status, dining_hall.name, user.user_id, user.user_id, dining_hall.name, inventory_item.item_id, minutes), True)
		return
	
	def exists_review_with_id(self, review_id : int):
		return self.__single_row("SELECT {params} FROM review WHERE id=%s", 
								{"COUNT(1)": "count"},
								(review_id,),
								lambda row : row["count"] > 0)
	
	def exists_review(self, serves_id : int, user : objects.User):
		return self.__single_row("SELECT {params} FROM review WHERE item=%s AND user=%s", 
								{"COUNT(1)": "count"},
								(serves_id, user.user_id), 
								lambda row : row["count"] > 0)

	def reviews_for(self, served_menu_item : objects.MenuItemServed):
		return self.__multiple_rows("SELECT {params} FROM review LEFT JOIN serves ON serves.id=review.item LEFT JOIN user ON user.id=review.user WHERE serves.menu_item_id=%s ORDER BY review.id DESC",
								{"review.id": "review.id", "review.rating": "review.rating", "review.comments": "review.comments", "user.id": "user.id", "user.name": "user.name", "user.role": "user.role"},
								(served_menu_item.menu_item.menu_item_id,),
								lambda row : objects.Review.from_db(row, served_menu_item))

	def add_alert(self, user : objects.User, menu_item_id):
		self._query("INSERT INTO alert(user, menu_item_id) SELECT %s, %s FROM DUAL WHERE (SELECT COUNT(1) FROM alert WHERE user=%s AND menu_item_id=%s)=0", (user.user_id, menu_item_id, user.user_id, menu_item_id), True)
		return

	def alerts_for(self, user : objects.User):
		return self.__multiple_rows("SELECT {params} FROM alert LEFT JOIN menu_item ON menu_item.id=alert.menu_item_id WHERE alert.user=%s",
								{"alert.id": "alert.id", "menu_item.id": "menu_item.id", "menu_item.name": "menu_item.name"},
								(user.user_id, ),
								lambda row : objects.AlertSubscription.from_db(row, user))

	def remove_alert(self, alert_id : objects.AlertSubscription, user : objects.User):
		self._query("DELETE FROM alert WHERE id=%s AND user=%s", (alert_id, user.user_id), True)
		return
