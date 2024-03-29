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
from datetime import datetime, time, timedelta
from page_behaviors import dining_hall_page, add_alert, add_review, add_status, alerts_page, delete_review, remove_alert,\
    view_reviews, send_contact, metrics
import flask
import werkzeug

db_connection = db.DBConnector();
        
class ObjectModelTests(unittest.TestCase):
    #get Leutner
    leutner = objects.DiningHall.from_list(db_connection.dining_halls(), "Leutner")
    
    def test_object_database_interactions(self):
        #create a menu item
        menu_item_id = random.randint(1, 100000)
        menu_item_name = f"MenuItem{menu_item_id}"
        
        db_connection._query("INSERT INTO menu_item(id, name) VALUES(%s, %s)", (menu_item_id, menu_item_name), True)
        db_connection._query("INSERT INTO serves(date_of, menu_item_id, meal, dining_hall_name) VALUES(%s, %s, %s, %s)", (datetime.today().date(), menu_item_id, "dinner", "Leutner"), True)
        
        #make sure it can be retrieved
        menu = self.leutner.menu(datetime.today().date(), "dinner", db_connection)
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
        review_text = "test review %s" % random.randint(1, 100000)
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
        inventory_item_name = "Inventory Item %s" % random.randint(1, 100000)
        db_connection._query("INSERT INTO inventory_item(id, name) VALUES(%s, %s)", (inventory_item_id, inventory_item_name, ), True)
        
        def get_inventory():
            return [inventory_item_status for inventory_item_status in self.leutner.inventory(1, db_connection) if inventory_item_status.item.item_id == inventory_item_id]
        
        inventory = get_inventory()
        self.assertEqual(len(inventory), 1, "inventory status not listed")
        self.assertEqual(inventory[0].status_str, "Unknown", "status should not be set")
        
        db_connection.add_status(self.leutner, inventory[0].item, 3, test_user, 15)
        inventory = get_inventory()
        self.assertEqual(inventory[0].status_str, "Available", "status should be available")
        
        db_connection.add_status(self.leutner, inventory[0].item, 0, test_user, 15)
        inventory = get_inventory()
        self.assertEqual(inventory[0].status_str, "Available", "status should be updated twice")
        
    def test_alerts(self):
        result = db_connection._query("SELECT id FROM serves")
        item = db_connection.served_item(result[0][0])
        
        db_connection.add_alert(FakeLoggedInState.user, item.menu_item.menu_item_id)
        
        self.assertTrue(item.menu_item.menu_item_id in [alert.menu_item.menu_item_id for alert in db_connection.alerts_for(FakeLoggedInState.user)], "failed to add alert")
        
        alert = [alert for alert in db_connection.alerts_for(FakeLoggedInState.user) if alert.menu_item.menu_item_id == item.menu_item.menu_item_id][0]
        db_connection.remove_alert(alert.alert_id, FakeLoggedInState.user)
        self.assertFalse(item.menu_item.menu_item_id in [alert.menu_item.menu_item_id for alert in db_connection.alerts_for(FakeLoggedInState.user)], "failed to remove alert")
        
    def test_dining_hall(self):
        fake_dining_hall = objects.DiningHall("Not Fribley", {
            "meal1": (time(10, 0, 0), time(12, 0, 0)),
            "meal2": (time(14, 0, 0), time(16, 0, 0))
            })
        
        self.assertEqual(fake_dining_hall.next_meal_after(time(9, 0, 0)), ("meal1", datetime.today().date()), "DiningHall.next_meal_after failed for when no meals have occurred yet")
        self.assertEqual(fake_dining_hall.next_meal_after(time(11, 0, 0)), ("meal1", datetime.today().date()), "DiningHall.next_meal_after failed during mealtime")
        self.assertEqual(fake_dining_hall.next_meal_after(time(13, 0, 0)), ("meal2", datetime.today().date()), "DiningHall.next_meal_after failed between meals")
        self.assertEqual(fake_dining_hall.next_meal_after(time(14, 0, 0)), ("meal2", datetime.today().date()), "DiningHall.next_meal_after failed at beginning of meal")
        self.assertEqual(fake_dining_hall.next_meal_after(time(15, 0, 0)), ("meal2", datetime.today().date()), "DiningHall.next_meal_after failed during second meal")
        self.assertEqual(fake_dining_hall.next_meal_after(time(16, 0, 1)), ("meal1", (datetime.today() + timedelta(days=1)).date()), "DiningHall.next_meal_after failed for when last meal is over")
        
class FakeNotLoggedInState:        
    user = None

class FakeLoggedInState:
    user = objects.User("abc123", "Test User", "user")
    
class FakeAdminState:
    user = objects.User("abc123", "Test User", "admin")
        
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
                
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="delete review page failed to reject non-existent reviews"):
            with mock.patch("page_behaviors.delete_review.request", m):
                delete_review.preempt(db_connection, {"login_state": FakeAdminState()})
        
        result = db_connection._query("SELECT id FROM review", ())
        
        m.form["review_id"] = result[0][0]
                
        with mock.patch("page_behaviors.delete_review.request", m):
            self.assertEqual(delete_review.preempt(db_connection, {"login_state": FakeAdminState()}), None, "delete review rejects valid request")
            
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
            
    def test_metrics_page(self):
        m = mock.MagicMock()
        m.args = {}
        
        with mock.patch("libs.funcs.request", m):
            with mock.patch("page_behaviors.metrics.request", m):
                with self.assertRaises(werkzeug.exceptions.NotFound, msg="metrics page failed to reject not-logged-in user"):
                    metrics.preempt(db_connection, {"login_state": FakeNotLoggedInState()})
                    
                with self.assertRaises(werkzeug.exceptions.NotFound, msg="metrics page failed to reject non-admin"):
                    metrics.preempt(db_connection, {"login_state": FakeLoggedInState()})
                    
                m.args["inventory"] = -1
                with self.assertRaises(werkzeug.exceptions.NotFound, msg="metrics page failed to reject non-existent food item"):
                    metrics.preempt(db_connection, {"login_state": FakeAdminState()})
                
                m.args["inventory"] = db_connection.all_inventory_items()[0].item_id
                self.assertEqual(metrics.preempt(db_connection, {"login_state": FakeAdminState()}), None, "metrics page failed to accept admin with valid inventory item")
                
                m.args = {}
                self.assertEqual(metrics.preempt(db_connection, {"login_state": FakeAdminState()}), None, "metrics page failed to accept admin with no inventory item")
            
    def test_remove_alert_page(self):
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="remove alert page failed to reject not logged in user"):
            remove_alert.preempt(db_connection, {"login_state": FakeNotLoggedInState()}, 1)
            
        self.assertEqual(remove_alert.preempt(db_connection, {"login_state": FakeLoggedInState()}, 1), None, "remove alert page failed to accept valid user")
      
    def test_send_contact(self):
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="send contact page failed to reject not logged in user"):
            send_contact.preempt(db_connection, {"login_state": FakeNotLoggedInState()})
            
        m = mock.MagicMock()
        m.form = {}    
        
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="send contact page failed to missing title"):
            with mock.patch("page_behaviors.send_contact.request", m):
                send_contact.preempt(db_connection, {"login_state": FakeLoggedInState()})
        
        m.form = {"title": "Title"}
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="send contact page failed to missing comment"):
            with mock.patch("page_behaviors.send_contact.request", m):
                send_contact.preempt(db_connection, {"login_state": FakeLoggedInState()})
                
        m.form = {"title": "Title", "comment": "Comment"}
        with mock.patch("page_behaviors.send_contact.request", m):
            self.assertEqual(send_contact.preempt(db_connection, {"login_state": FakeLoggedInState()}), None, "send contact page failed to accept valid request")
        
    def test_view_reviews_page(self):
        m = mock.MagicMock()
        m.args = {"page": "1"}
        
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="view reviews page failed to reject invalid ID"):
            with mock.patch("page_behaviors.view_reviews.request", m):
                view_reviews.preempt(db_connection, {}, -1)
        
        result = db_connection._query("SELECT id FROM menu_item")
        item_id = result[0][0]
        
        with mock.patch("page_behaviors.view_reviews.request", m):
            self.assertEqual(view_reviews.preempt(db_connection, {}, item_id), None, "view reviews page failed to accept valid ID")
        
        m.args = {"page": "10000"}
        with self.assertRaises(werkzeug.exceptions.NotFound, msg="view reviews page failed to reject invalid page"):
            with mock.patch("page_behaviors.view_reviews.request", m):
                view_reviews.preempt(db_connection, {}, -1)
        
class PageDataTests(unittest.TestCase):
    leutner = objects.DiningHall.from_list(db_connection.dining_halls(), "Leutner")
    
    def __init__(self):
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
        m = mock.MagicMock()
        m.args = {"meal": "lunch"}
        
        with mock.patch("page_behaviors.dining_hall_page.request", m): 
            with mock.patch("libs.funcs.request", m): 
                self.assertEqual(dining_hall_page.page_data(db_connection, {"dining_halls": db_connection.dining_halls()}, "Leutner")["dining_hall"].name, "Leutner", "dining hall page got wrong dining hall")        
                self.assertEqual(dining_hall_page.page_data(db_connection, {"dining_halls": db_connection.dining_halls()}, "Leutner")["meal"], "lunch", "dining hall page got wrong meal")        
                m.args["meal"] = "dinner"
                self.assertEqual(dining_hall_page.page_data(db_connection, {"dining_halls": db_connection.dining_halls()}, "Leutner")["meal"], "dinner", "dining hall page got wrong meal")
            
                m.args["date"] = "2019-01-02"
                self.assertEqual(dining_hall_page.page_data(db_connection, {"dining_halls": db_connection.dining_halls()}, "Leutner")["date"].day, 2, "dining hall page got wrong day")
                self.assertEqual(dining_hall_page.page_data(db_connection, {"dining_halls": db_connection.dining_halls()}, "Leutner")["date"].month, 1, "dining hall page got wrong month")
                self.assertEqual(dining_hall_page.page_data(db_connection, {"dining_halls": db_connection.dining_halls()}, "Leutner")["date"].year, 2019, "dining hall page got wrong date")
                
                m.args["date"] = "randomstringofgarbage"
                self.assertEqual(dining_hall_page.page_data(db_connection, {"dining_halls": db_connection.dining_halls()}, "Leutner")["date"].day, datetime.today().day, "dining hall page didn't ignore invalid date")
        
        return
    
    def test_view_reviews_page(self):
        m = mock.MagicMock()
        
        result = db_connection._query("SELECT id FROM menu_item")
        item_id = result[0][0]
        
        db_mock = mock.MagicMock()
        db_mock.reviews_for = lambda reviews : range(95)
        m.args = {"page": "1"}
        with mock.patch("page_behaviors.view_reviews.request", m):
            self.assertEqual(len(view_reviews.page_data(db_mock, {}, item_id)["reviews"]), 20, "failed to paginate properly for view_reviews page")
            m.args = {"page": "5"}
            self.assertEqual(len(view_reviews.page_data(db_mock, {}, item_id)["reviews"]), 15, "failed to paginate properly for view_reviews page")
            self.assertEqual(view_reviews.page_data(db_mock, {}, item_id)["reviews"][0], 80, "failed to paginate properly for view_reviews page")
        
        return
