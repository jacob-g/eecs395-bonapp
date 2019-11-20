from builtins import staticmethod
import datetime

class DiningHall:
	def __init__(self, name : str, hours : dict):
		self.name : str = name
		self.hours = hours
		
	@staticmethod
	def __str_range_to_time(time_str):
		return tuple([datetime.datetime.strptime(time, "%I:%M %p").time() for time in time_str.split(" - ")])
		
	@staticmethod
	def from_db(row : dict):
		hours = dict([
			(
				meal_info[0].replace("dining_hall.meal.", "", 1),
				DiningHall.__str_range_to_time(meal_info[1]) if meal_info[1] is not None else None
		  	)
			for meal_info in row.items() 
			if meal_info[0].startswith("dining_hall.meal.")
		])
			
		return DiningHall(row["dining_hall.name"], hours)
	
	@staticmethod
	def from_list(dining_hall_list : list, dining_hall_name : str):
		dining_hall_candidates : list[DiningHall] = [dining_hall for dining_hall in dining_hall_list if dining_hall.name == dining_hall_name]
		if len(dining_hall_candidates) == 0:
			return None
		else:
			return dining_hall_candidates[0]
		
	def menu(self, date : datetime.date, meal : str, db):
		return db.menu_for(self, date, meal)
		
	def inventory(self, minutes : int, db):
		return db.inventory_for(self, minutes)
	
	def next_meal_after(self, time : datetime.time):
		later_meals = [meal[0]
					for meal 
					in self.hours.items() 
					if meal[1] is not None and meal[1][1] > time]
		return (later_meals[0], datetime.date.today()) if len(later_meals) > 0 else (next(iter(self.hours)), (datetime.date.today() + datetime.timedelta(days=1)))
	
class InventoryItem:
	def __init__(self, item_id : int, name : str):
		self.item_id : int = item_id
		self.name : str = name
		
	@staticmethod
	def from_db(row : dict):
		return InventoryItem(row["inventory_item.id"], row["inventory_item.name"])

class InventoryStatus:
	def __init__(self, item : InventoryItem, dining_hall : DiningHall, status : float):
		self.item : InventoryItem = item
		self.status : float = status
		self.status_str = InventoryStatus.status_str_of(self.status)
		self.dining_hall : DiningHall = dining_hall
		
	@staticmethod
	def status_str_of(status : float):
		if status is None:
			return "Unknown"
		elif status <= 1:
			return "Not available"
		elif status <= 2:
			return "Limited"
		else:
			return "Available"
	
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
	def __init__(self, user_id : str, name : str, role : str = "user"):
		self.user_id : str = user_id
		self.name : str = name
		self.role : str = role
		
	def to_dictionary(self):
		return {"id": self.user_id, "name": self.name, "role": self.role}
	
	def add_to_db(self, db):
		return db.add_user_if_not_exists(self)
	
	@staticmethod
	def from_db(row : dict):
		return User(row["user.id"], row["user.name"], row["user.role"])
	
	@staticmethod
	def from_dictionary(in_dict : dict):
		return User(in_dict["id"], in_dict["name"], in_dict["role"])
	
class Review:
	def __init__(self, review_id : int, rating : int, comments : str, menu_item : MenuItemServed, reviewer : User):
		self.review_id : int = review_id
		self.rating : int = rating
		self.comments : str = comments
		self.menu_item : MenuItemServed = menu_item
		self.reviewer : User = reviewer
	
	@staticmethod
	def from_db(row : tuple, menu_item : MenuItemServed):
		return Review(row["review.id"], row["review.rating"], row["review.comments"], menu_item, User.from_db(row))
	
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