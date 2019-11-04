'''
Created on Oct 24, 2019

@author: Jacob
'''

import unittest
import random
from libs import db
from libs import objects

db_connection = db.DBConnector();

class UserTest(unittest.TestCase):
    def test_add_user(self):
        db_connection.add_user_if_not_exists(objects.User("abc123", "Test User"))
        db_connection.add_user_if_not_exists(objects.User("abc123", "Test User 2"))
        
        self.assertEqual(db_connection.user_for("abc123").name, "Test User", "User is only added once")
        
class MenuItemTest(unittest.TestCase):
    def test_add_menu_item(self):
        menu_item_id = random.randint(1, 100000)
        menu_item_name = f"MenuItem{menu_item_id}"
        
        db_connection.__query("INSERT INTO menu_item(id, name) VALUES(%s, %s)", (menu_item_id, menu_item_name), True)
        db_connection.__query("INSERT INTO serves")