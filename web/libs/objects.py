class DiningHall:
	def __init__(self, name):
		self.name = name
		
	def menu(self, date, db):
		return db.menuFor(self, date)
		
	def inventory(self, time):
		return
		
class MenuItem:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		
class Review:
	def __init__(self, rating, comments):
		self.rating = rating
		self.comments = comments

#TODO: make JSON-serializable
class User:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		
	def to_dictionary(self):
		return {"id": self.id, "name": self.name}
	
	@staticmethod
	def from_dictionary(in_dict):
		return User(in_dict["id"], in_dict["name"])