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
from page_behaviors import dining_hall_page, add_alert, add_review, add_status, alerts_page, delete_review, remove_alert,\
    view_reviews
import flask
import werkzeug

db_connection = db.DBConnector();
        
class ObjectModelTests(unittest.TestCase):
    def test_object_database_interactions(self):
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
        
    def test_delete_review_page(self):
        m = mock.MagicMock()
        
        m.form = {"review_id": -1}
        
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="delete review page failed to reject not logged in users"):
            with mock.patch("page_behaviors.delete_review.request", m):
                delete_review.preempt(db_connection, {"login_state": FakeNotLoggedInState()})
                
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="delete review page failed to reject non-admin users"):
            with mock.patch("page_behaviors.delete_review.request", m):
                delete_review.preempt(db_connection, {"login_state": FakeLoggedInState()})
                
        admin = FakeLoggedInState();
        admin.user.role = "admin"
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="delete review page failed to reject non-existent reviews"):
            with mock.patch("page_behaviors.delete_review.request", m):
                delete_review.preempt(db_connection, {"login_state": admin})
        
        result = db_connection._query("SELECT id FROM review", ())
        
        m.form["review_id"] = result[0][0]
                
        with mock.patch("page_behaviors.delete_review.request", m):
            self.assertEqual(delete_review.preempt(db_connection, {"login_state": admin}), None, "delete review rejects valid request")
            
    def test_dining_hall_page(self):
        m = mock.MagicMock()
        m.args = {}
        
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="dining hall page failed to reject invalid dining halls"):
            with mock.patch("page_behaviors.dining_hall_page.request", m):
                dining_hall_page.preempt(db_connection, {"dining_halls": db_connection.dining_halls()}, "DININGHALLTHATDOESN'TEXIST")
        
        m.args["meal"] = "secondbreakfast"
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="dining hall page failed to reject invalid meals"):
            with mock.patch("page_behaviors.dining_hall_page.request", m):
                dining_hall_page.preempt(db_connection, {"dining_halls": db_connection.dining_halls()}, "Leutner")
        
        
        with mock.patch("page_behaviors.dining_hall_page.request", m):
            m.args["meal"] = "dinner"
            self.assertEqual(dining_hall_page.preempt(db_connection, {"dining_halls": db_connection.dining_halls()}, "Leutner"), None, "dining hall page failed to accept valid meal")
            
            del m.args["meal"]
            self.assertEqual(dining_hall_page.preempt(db_connection, {"dining_halls": db_connection.dining_halls()}, "Leutner"), None, "dining hall page failed to accept no meal provided")
            
    def test_remove_alert_page(self):
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="remove alert page failed to reject not logged in user"):
            remove_alert.preempt(db_connection, {"login_state": FakeNotLoggedInState()}, 1)
            
        self.assertEqual(remove_alert.preempt(db_connection, {"login_state": FakeLoggedInState()}, 1), None, "remove alert page failed to accept valid user")
        
    def test_view_reviews_page(self):
        m = mock.MagicMock()
        m.args = {"page": "1"}
        
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="view reviews page failed to reject invalid ID"):
            with mock.patch("page_behaviors.view_reviews.request", m):
                view_reviews.preempt(db_connection, {}, -1)
        
        result = db_connection._query("SELECT id FROM menu_item")
        item_id = result[0][0]
        
        self.assertEqual(view_reviews.preempt(db_connection, {}, item_id), None, "view reviews page failed to accept valid ID")
        with mock.patch("page_behaviors.view_reviews.request", m):
            self.assertEqual(view_reviews.preempt(db_connection, {}, item_id), None, "view reviews page failed to accept valid ID")
        
        m.args = {"page": "10000"}
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="view reviews page failed to reject invalid page"):
            with mock.patch("page_behaviors.view_reviews.request", m):
                view_reviews.preempt(db_connection, {}, -1)
                
        db_mock = mock.MagicMock()
        db_mock.reviews_for = lambda reviews : range(95)
        m.args = {"page": "1"}
        with mock.patch("page_behaviors.view_reviews.request", m):
            self.assertEqual(len(view_reviews.page_data(db_mock, {}, item_id)["reviews"]), 20, "failed to paginate properly for view_reviews page")
            m.args = {"page": "5"}
            self.assertEqual(len(view_reviews.page_data(db_mock, {}, item_id)["reviews"]), 15, "failed to paginate properly for view_reviews page")
            self.assertEqual(view_reviews.page_data(db_mock, {}, item_id)["reviews"][0], 80, "failed to paginate properly for view_reviews page")
        
class PageDataTests(unittest.TestCase):
    leutner = objects.DiningHall.from_list(db_connection.dining_halls(), "Leutner")
    
    def __init__(self):
        user_id = "user%d".format(random.randint(1, 100000))
        db_connection.add_user_if_not_exists(FakeLoggedInState.user)
    
    def test_alerts_page(self):
        result = db_connection._query("SELECT id FROM menu_item ORDER BY RAND()")
        item_id = result[0][0]
        
        db_connection.add_alert(self.user, item_id)
        
        alerted_items = [alert.menu_item.menu_item_id for alert in alerts_page.page_data(db_connection, {"login_state": FakeLoggedInState()})["alert_subscriptions"]]
        menu_ids = [menu_item.menu_item_id for menu_item in alerts_page.page_data(db_connection, {"login_state": FakeLoggedInState()})["all_menu_items"]]
        
        self.assertIn(item_id, alerted_items, "alerts page does not contain ID for added alert")
        self.assertIn(item_id, menu_ids, "alerts page has incomplete menu")
        
    def test_dining_hall_page(self):
        return #TODO: implement this
    
    def test_view_reviews_page(self):
        return #TODO: implement this
