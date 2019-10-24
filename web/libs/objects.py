from builtins import staticmethod
import datetime

class InventoryItem:
	def __init__(self, item_id : int, name : str):
		self.item_id = item_id
		self.name = name
		
	@staticmethod
	def from_db(row : dict):
		return InventoryItem(row["inventory_item.id"], row["inventory_item.name"])

class InventoryStatus:
	def __init__(self, item : InventoryItem, status : int):
		self.item = item
		self.status = status

class DiningHall:
	def __init__(self, name : str):
		self.name = name
		
	@staticmethod
	def from_db(row : dict):
		return DiningHall(format(row["dining_hall.name"]))
	
	@staticmethod
	def from_list(dining_hall_list : list, dining_hall_name : str):
		dining_hall_candidates = [dining_hall for dining_hall in dining_hall_list if dining_hall.name == dining_hall_name]
		if len(dining_hall_candidates) == 0:
			return None
		else:
			return dining_hall_candidates[0]
		
	def menu(self, date : datetime.date, db):
		return db.menu_for(self, date)
		
	def inventory(self, minutes : int, db):
		return db.inventory_for(self, minutes)
	
class MenuItem:
	def __init__(self, menu_item_id : int, name : str, dining_hall : DiningHall):
		self.id = menu_item_id
		self.name = name
		self.dining_hall = dining_hall
		
	@staticmethod
	def from_db(row : tuple, dining_hall : DiningHall):
		return MenuItem(row["menu_item.id"], row["menu_item.name"], dining_hall)	
	
class MenuItemServed:
	def __init__(self, serve_id : int, menu_item : MenuItem, meal : str):
		self.serve_id = serve_id
		self.menu_item = menu_item
		self.meal = meal
		
	@staticmethod
	def from_db(row : dict, dining_hall : DiningHall):
		return MenuItemServed(row["serves.id"], MenuItem.from_db(row, dining_hall), row["serves.meal"])
	
class User:
	def __init__(self, user_id : str, name : str):
		self.user_id = user_id
		self.name = name
		
	def to_dictionary(self):
		return {"id": self.user_id, "name": self.name}
	
	def add_to_db(self, db):
		return db.add_user_if_not_exists(self)
	
	@staticmethod
	def from_dictionary(in_dict : dict):
		return User(in_dict["id"], in_dict["name"])
	
class Review:
	def __init__(self, rating : int, comments : str, menu_item : MenuItem, reviewer : User):
		self.rating = rating
		self.comments = comments
		self.menu_item = menu_item
		self.reviewer = reviewer
	
	@staticmethod
	def from_db(row : tuple, menu_item : MenuItem):
		return Review(row["review.rating"], row["review.comments"], menu_item, User(row["user.id"], row["user.name"]))
	
	def add_to_db(self, db):
		return db.add_review(self)

class AlertSubscription:
	def __init__(self, user : User, menu_item : MenuItem):
		self.user = user
		self.menu_item = menu_item
		
	@staticmethod
	def from_db(self, row : tuple):
		#TODO: implement
		return None