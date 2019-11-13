'''
Created on Oct 24, 2019

@author: Jacob
'''

import unittest
import random
from libs import db
from libs import objects
from datetime import datetime
from page_behaviors import dining_hall_page, add_alert
from flask import abort, request
import werkzeug

db_connection = db.DBConnector();
        
class MenuItemTest(unittest.TestCase):
    def test_add_menu_item(self):
        #get Leutner
        leutner = objects.DiningHall.from_list(db_connection.dining_halls(), "Leutner")
        
        #create a menu item
        menu_item_id = random.randint(1, 100000)
        menu_item_name = f"MenuItem{menu_item_id}"
        
        db_connection._query("INSERT INTO menu_item(id, name) VALUES(%s, %s)", (menu_item_id, menu_item_name), True)
        db_connection._query("INSERT INTO serves(date_of, menu_item_id, meal, dining_hall_name) VALUES(%s, %s, %s, %s)", (datetime.today().date(), menu_item_id, "dinner", "Leutner"), True)
        
        #make sure it can be retrieved
        menu = leutner.menu(datetime.today().date(), "dinner", db_connection)
        served_items = [served_item for served_item in menu if served_item.menu_item.menu_item_id == menu_item_id]
        
        self.assertEqual(len(served_items), 1, "menu item not added and marked as served properly")
        
        served_item = db_connection.served_item(served_items[0].serve_id)
        self.assertNotEqual(served_item, None, "could not get served item on its own")
        
        #create a user
        user_id = "user%d".format(random.randint(1, 100000))
        db_connection.add_user_if_not_exists(objects.User(user_id, "Test User"))
        db_connection.add_user_if_not_exists(objects.User(user_id, "Test User 2"))
        
        test_user = db_connection.user_for(user_id)
        self.assertEqual(test_user.name, "Test User", "User is only added once")
        
        #leave a review
        rating_num = random.randint(1, 5)
        review_text = "test review %i".format(random.randint(1, 100000))
        db_connection.add_review(test_user, rating_num, review_text, served_item.serve_id)
        reviews = db_connection.reviews_for(served_item)
        self.assertEqual(len(reviews), 1, "review not properly added")
        review = reviews[0]
        self.assertEqual(review.rating, rating_num, "review rating is incorrect")
        self.assertEqual(review.comments, review_text, "review comment is incorrect")
        
        #delete the review
        db_connection.delete_review(review.review_id)
        self.assertEqual(len(db_connection.reviews_for(served_item)), 0, "review not properly deleted")
        
        #create some random inventory item
        inventory_item_id = random.randint(1, 100000)
        inventory_item_name = "Inventory Item %i".format(random.randint(1, 100000))
        db_connection._query("INSERT INTO inventory_item(id, name) VALUES(%s, %s)", (inventory_item_id, inventory_item_name, ), True)
        
        def get_inventory():
            return [inventory_item_status for inventory_item_status in leutner.inventory(1, db_connection) if inventory_item_status.item.item_id == inventory_item_id]
        
        inventory = get_inventory()
        self.assertEqual(len(inventory), 1, "inventory status not listed")
        self.assertEqual(inventory[0].status_str, "Unknown", "status should not be set")
        
        db_connection.add_status(leutner, inventory[0].item, 3, test_user, 15)
        inventory = get_inventory()
        self.assertEqual(inventory[0].status_str, "Available", "status should be available")
        
        db_connection.add_status(leutner, inventory[0].item, 0, test_user, 15)
        inventory = get_inventory()
        self.assertEqual(inventory[0].status_str, "Available", "status should be updated twice")
        
class FakeRequest:
    def __init__(self, form):
        self.request = form
        
        
class PreemptTests(unittest.TestCase):
    def test_dining_hall(self):
        with self.assertRaises(werkzeug.exceptions.NotFound):
            self.assertEqual(dining_hall_page.preempt(db_connection, {"dining_halls": db_connection.dining_halls()}, "NONEXISTENTDININGHALL"), abort(404))
        self.assertEqual(dining_hall_page.preempt(db_connection, {"dining_halls": db_connection.dining_halls()}, "Leutner"), None)
        
    def test_add_alert(self):
        #TODO: mock a Flask request