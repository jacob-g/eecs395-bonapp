'''
Created on Oct 24, 2019

@author: Jacob
'''

import unittest
import random
import mock
from pytest_mock import mocker
from libs import db
from libs import objects
from datetime import datetime
from page_behaviors import dining_hall_page, add_alert, add_review, add_status, alerts_page
import flask
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
        
class FakeNotLoggedInState:        
    user = None

class FakeLoggedInState:
    user = objects.User("abc123", "Test User", "user")
        
class PreemptTests(unittest.TestCase):
    leutner = objects.DiningHall.from_list(db_connection.dining_halls(), "Leutner")
    menu = leutner.menu(datetime.today().date(), "dinner", db_connection)
    menu_item_id = menu[0].menu_item.menu_item_id
    
    def test_dining_hall(self):
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="dining hall page failed to reject non-existent dining hall"):
            dining_hall_page.preempt(db_connection, {"dining_halls": db_connection.dining_halls()}, "NONEXISTENTDININGHALL")
        self.assertEqual(dining_hall_page.preempt(db_connection, {"dining_halls": db_connection.dining_halls()}, "Leutner"), None, "dining hall page failed to allow valid dining hall")
        
    def test_add_alert(self):
        m = mock.MagicMock()
        
        m.form = {"food": None}
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="add alert failed to gracefully reject non-existent food item"):
            with mock.patch("page_behaviors.add_alert.request", m):
                add_alert.preempt(db_connection, {})
        
        m.form = {"food": -1}
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="add alert failed to reject invalid food item"):
            with mock.patch("page_behaviors.add_alert.request", m):
                add_alert.preempt(db_connection, {})
        
        m.form = {"food": self.menu_item_id}
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="add alert failed to reject not logged in user"):
            with mock.patch("page_behaviors.add_alert.request", m):
                add_alert.preempt(db_connection, {"login_state": FakeNotLoggedInState()})
                
        with mock.patch("page_behaviors.add_alert.request", m):        
            self.assertEqual(add_alert.preempt(db_connection, {"login_state": FakeLoggedInState()}), None, "failed to add alert with valid data")
            
    def test_add_review(self):
        m = mock.MagicMock()
        
        m.form = {"serves_id": -1}
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="add review failed to reject non-existent menu item"):
            with mock.patch("page_behaviors.add_review.request", m):
                add_review.preempt(db_connection, {})
                
        m.form = {"serves_id": self.menu[0].serve_id}
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="add review failed to reject not logged in user"):
            with mock.patch("page_behaviors.add_review.request", m):
                add_review.preempt(db_connection, {"login_state": FakeNotLoggedInState()})
        
        #TODO: add a test for an already existing review
        
        with mock.patch("page_behaviors.add_review.request", m):
            self.assertEqual(add_review.preempt(db_connection, {"login_state": FakeLoggedInState()}), None, "add review rejected valid request")
            
    def test_add_status(self):
        m = mock.MagicMock()
        
        m.form = {"dining_hall_name": "dining hall that does not exist", "amenity_id": -1}
        
        dining_halls = db_connection.dining_halls()
        
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="add status page failed to reject not logged in user"):
            with mock.patch("page_behaviors.add_status.request", m):
                add_status.preempt(db_connection, {"login_state": FakeNotLoggedInState(), "dining_halls": dining_halls})
                
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="add status page failed to reject non-existent dining hall"):
            with mock.patch("page_behaviors.add_status.request", m):
                add_status.preempt(db_connection, {"login_state": FakeLoggedInState(), "dining_halls": dining_halls})
                
        m.form["dining_hall_name"] = "Leutner"
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="add status failed to reject non-existent amenity id"):
            with mock.patch("page_behaviors.add_status.request", m):
                add_status.preempt(db_connection, {"login_state": FakeLoggedInState(), "dining_halls": dining_halls})
                
        real_item = db_connection.inventory_for(self.leutner, 30)[0].item
        m.form["amenity_id"] = real_item.item_id
        with mock.patch("page_behaviors.add_status.request", m):
            self.assertEqual(add_status.preempt(db_connection, {"login_state": FakeLoggedInState(), "dining_halls": dining_halls}), None, "add status page failed to allow valid request")
            
    def test_alerts_page(self):
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="alerts page failed to reject not logged in users"):
            alerts_page.preempt(db_connection, {"login_state": FakeNotLoggedInState()})
            
        self.assertEqual(alerts_page.preempt(db_connection, {"login_state": FakeLoggedInState()}), None, "alerts page failed to allow logged in users")