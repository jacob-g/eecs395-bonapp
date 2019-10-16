from builtins import staticmethod
class InventoryItem:
	def __init__(self, item_id, name):
		self.item_id = item_id
		self.name = name
		
	@staticmethod
	def from_db(row):
		return InventoryItem(row["inventory_item.id"], row["inventory_item.name"])

class InventoryStatus:
	def __init__(self, item, status):
		self.item = item
		self.status = status

class DiningHall:
	def __init__(self, name):
		self.name = name
		
	@staticmethod
	def from_db(row):
		return DiningHall(format(row["dining_hall.name"]))
	
	@staticmethod
	def from_list(dining_hall_list, dining_hall_name):
		dining_hall_candidates = [dining_hall for dining_hall in dining_hall_list if dining_hall.name == dining_hall_name]
		if len(dining_hall_candidates) == 0:
			return None
		else:
			return dining_hall_candidates[0]
		
	def menu(self, date, db):
		return db.menu_for(self, date)
		
	def inventory(self, minutes, db):
		return db.inventory_for(self, minutes)
	
class MenuItemServed:
	def __init__(self, serve_id, menu_item, meal):
		self.serve_id = serve_id
		self.menu_item = menu_item
		self.meal = meal
		
	@staticmethod
	def from_db(row, dining_hall):
		return MenuItemServed(row["serves.id"], MenuItem.from_db(row, dining_hall), row["serves.meal"])
		
class MenuItem:
	def __init__(self, id, name, dining_hall):
		self.id = id
		self.name = name
		self.dining_hall = dining_hall
		
	@staticmethod
	def from_db(row, dining_hall):
		return MenuItem(row["menu_item.id"], row["menu_item.name"], dining_hall)	
	
class Review:
	def __init__(self, rating, comments, menu_item, reviewer):
		self.rating = rating
		self.comments = comments
		self.menu_item = menu_item
		self.reviewer = reviewer
	
	@staticmethod
	def from_db(row, menu_item):
		return Review(row["review.rating"], row["review.comments"], menu_item, User(row["user.id"], row["user.name"]))
	
	def add_to_db(self, db):
		return db.add_review(self)

class User:
	def __init__(self, user_id, name):
		self.user_id = user_id
		self.name = name
		
	def to_dictionary(self):
		return {"id": self.id, "name": self.name}
	
	def add_to_db(self, db):
		return db.add_user_if_not_exists(self)
	
	@staticmethod
	def from_dictionary(in_dict):
		return User(in_dict["id"], in_dict["name"])