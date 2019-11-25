import sys
import io
import unittest
import lxml.html
import lxml.etree as etree
import urllib.request
import mysql.connector
from WebScraper import write_to_db, insert_meal, serves_table, insert_hours

#read mock leutner menupage
page = open("static_menupage.htm", 'r', encoding='utf-8')

#retrieve page data
testtree = lxml.html.fromstring(page.read())

#retrieve hours
breakfastHours = testtree.xpath('//section[@data-jump-nav-title="Breakfast"]//div[@class="site-panel__daypart-time"]/text()')
brunchHours = testtree.xpath('//section[@data-jump-nav-title="Brunch"]//div[@class="site-panel__daypart-time"]/text()')
lunchHours = testtree.xpath('//section[@data-jump-nav-title="Lunch"]//div[@class="site-panel__daypart-time"]/text()')
dinnerHours = testtree.xpath('//section[@data-jump-nav-title="Dinner"]//div[@class="site-panel__daypart-time"]/text()')

#retrieve meals
breakfastItems = testtree.xpath('//section[@data-jump-nav-title="Breakfast"]//div[@class="c-tab__content site-panel__daypart-tab-content c-tab__content--active"]//button[@data-js="site-panel__daypart-item-title"]/text()')
brunchItems = testtree.xpath('//section[@data-jump-nav-title="Brunch"]//div[@class="c-tab__content site-panel__daypart-tab-content c-tab__content--active"]//button[@data-js="site-panel__daypart-item-title"]/text()')
lunchItems = testtree.xpath('//section[@data-jump-nav-title="Lunch"]//div[@class="c-tab__content site-panel__daypart-tab-content c-tab__content--active"]//button[@data-js="site-panel__daypart-item-title"]/text()')
dinnerItems = testtree.xpath('//section[@data-jump-nav-title="Dinner"]//div[@class="c-tab__content site-panel__daypart-tab-content c-tab__content--active"]//button[@data-js="site-panel__daypart-item-title"]/text()')

#connect to database
connection = mysql.connector.connect(host="localhost", user="bonapp", password="password", database="review")

class WebTests(unittest.TestCase):

    def test_read_tree(self):
        #test hours scraper
        self.assertEqual(breakfastHours[0].__str__(), "7:00 am - 10:30 am", "breakfast hours not scraped correctly")
        self.assertEqual(brunchHours, [], "brunch hours not scraped correctly")
        self.assertEqual(lunchHours[0].__str__(), "11:00 am - 2:45 pm", "lunch hours not scraped correctly")
        self.assertEqual(dinnerHours[0].__str__(), "5:00 pm - 8:00 pm", "dinner hours not scraped correctly")

        #test menu_item scraper
        self.assertEqual(breakfastItems[0].__str__().strip(), "Scrambled Harissa Tofu", "breakfast not scraped correctly")
        self.assertEqual(brunchItems, [], "brunch not scraped correctly")
        self.assertEqual(lunchItems[0].__str__().strip(), "Creamy Chicken Paprikash", "lunch not scraped correctly")
        self.assertEqual(dinnerItems[0].__str__().strip(), "Chicken with Preserved Lemon and Olives", "dinner not scraped correctly")


    def test_insert_hours(self):
        #write hours to databases
        insert_hours("Leutner", breakfastHours[0].__str__(), lunchHours[0].__str__(), dinnerHours[0].__str__(), None)

        #retrieve breakfast hours
        query = "select breakfast from dining_hall where name=%s"
        args = ("Leutner",)

        cursor = connection.cursor()
        cursor.execute(query,args)

        #check that breakfast hours were inserted correctly
        self.assertEqual(cursor.fetchall()[0][0],"7:00 am - 10:30 am", "breakfast hours not inserted correctly")

    def test_insert_meal(self):
        #write menu items to database
        write_to_db(breakfastItems, "Leutner", "Breakfast")
        write_to_db(brunchItems, "Leutner", "Lunch")
        write_to_db(lunchItems, "Leutner", "Lunch")
        write_to_db(dinnerItems, "Leutner", "Dinner")

    #def test_serves(self):


if __name__ == '__main__':
    unittest.main()
