class DiningHall:
	def __init__(self, name):
		self.name = name
		
	@staticmethod
	def from_db(row):
		return DiningHall(format(row["dining_hall.name"]))
		
	def menu(self, date, db):
		return db.menu_for(self, date)
		
	def inventory(self, time):
		return
		
class MenuItem:
	def __init__(self, id, name, dining_hall):
		self.id = id
		self.name = name
		self.dining_hall = dining_hall
		
	@staticmethod
	def from_db(row, dining_hall):
		return MenuItem(row["menu_item.id"], row["menu_item.name"], dining_hall)	
	
class Review:
	def __init__(self, rating, comments, menu_item):
		self.rating = rating
		self.comments = comments
		self.menu_item = menu_item
	
	@staticmethod
	def from_db(row, menu_item):
		return Review(row["review.rating"], row["review.comments"], menu_item)
	
	def add_to_db(self, db):
		return db.add_review(self)

class User:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		
	def to_dictionary(self):
		return {"id": self.id, "name": self.name}
	
	def add_to_db(self, db):
		return db.add_user_if_not_exists(self)
	
	@staticmethod
	def from_dictionary(in_dict):
		return User(in_dict["id"], in_dict["name"])