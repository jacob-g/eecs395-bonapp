from builtins import staticmethod
import datetime

class DiningHall:
	def __init__(self, name : str):
		self.name : str = name
		
	@staticmethod
	def from_db(row : dict):
		return DiningHall(format(row["dining_hall.name"]))
	
	@staticmethod
	def from_list(dining_hall_list : list, dining_hall_name : str):
		dining_hall_candidates : list[DiningHall] = [dining_hall for dining_hall in dining_hall_list if dining_hall.name == dining_hall_name]
		if len(dining_hall_candidates) == 0:
			return None
		else:
			return dining_hall_candidates[0]
		
	def menu(self, date : datetime.date, db):
		return db.menu_for(self, date)
		
	def inventory(self, minutes : int, db):
		return db.inventory_for(self, minutes)
	
class InventoryItem:
	def __init__(self, item_id : int, name : str):
		self.item_id : int = item_id
		self.name : str = name
		
	@staticmethod
	def from_db(row : dict):
		return InventoryItem(row["inventory_item.id"], row["inventory_item.name"])

class InventoryStatus:
	def __init__(self, item : InventoryItem, dining_hall : DiningHall, status : int):
		self.item : str = item
		self.status : int = status
		self.dining_hall : DiningHall = dining_hall
	
	@staticmethod
	def from_db(row : tuple, dining_hall : DiningHall):
		return InventoryStatus(InventoryItem.from_db(row), dining_hall, row["statuses.status"])
	
class MenuItem:
	def __init__(self, menu_item_id : int, name : str):
		self.menu_item_id : int = menu_item_id
		self.name : str = name
		
	@staticmethod
	def from_db(row : tuple):
		return MenuItem(row["menu_item.id"], row["menu_item.name"])	
	
class MenuItemServed:
	def __init__(self, serve_id : int, menu_item : MenuItem, meal : str, average_rating : float, dining_hall : DiningHall):
		self.serve_id : int = serve_id
		self.menu_item : MenuItem = menu_item
		self.meal : str = meal
		self.dining_hall : DiningHall = dining_hall
		self.average_rating = average_rating
		
	@staticmethod
	def from_db(row : dict, dining_hall : DiningHall):
		return MenuItemServed(row["serves.id"], MenuItem.from_db(row), row["serves.meal"], row["average_rating"], dining_hall)
	
class User:
	def __init__(self, user_id : str, name : str):
		self.user_id : str = user_id
		self.name : str = name
		
	def to_dictionary(self):
		return {"id": self.user_id, "name": self.name}
	
	def add_to_db(self, db):
		return db.add_user_if_not_exists(self)
	
	@staticmethod
	def from_dictionary(in_dict : dict):
		return User(in_dict["id"], in_dict["name"])
	
class Review:
	def __init__(self, rating : int, comments : str, menu_item : MenuItemServed, reviewer : User):
		self.rating : int = rating
		self.comments : str = comments
		self.menu_item : MenuItemServed = menu_item
		self.reviewer : User = reviewer
	
	@staticmethod
	def from_db(row : tuple, menu_item : MenuItemServed):
		return Review(row["review.rating"], row["review.comments"], menu_item, User(row["user.id"], row["user.name"]))
	
	def add_to_db(self, db):
		return db.add_review(self)

class AlertSubscription:
	def __init__(self, alert_id : int, user : User, menu_item : MenuItem):
		self.alert_id : int = alert_id
		self.user : User = user
		self.menu_item : MenuItem = menu_item
		
	@staticmethod
	def from_db(row : tuple, user : User):
		return AlertSubscription(row["alert.id"], user, MenuItem.from_db(row))