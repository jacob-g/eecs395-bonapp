import lxml.html
import lxml.etree
import requests
import mysql.connector
from datetime import datetime

#retrieve web page data
leutPage = requests.get("https://case.cafebonappetit.com/cafe/leutner-cafe/")
fribPage = requests.get("https://case.cafebonappetit.com/cafe/fribley-marche/")

#save html file
leutTree = lxml.html.fromstring(leutPage.content)
fribTree = lxml.html.fromstring(fribPage.content)

#connect to database
connection = mysql.connector.connect(host="localhost", user="bonapp", password="password", database="review")

#create relation serves
def serves_table(id, name, meal, date):
    query = "insert ignore into serves (menu_item_id, dining_hall_name, meal, date_of) values (%s, %s, %s, %s)"
    args = (id, name, meal, date)

    cursor = connection.cursor()
    cursor.execute(query,args)

    connection.commit()
    cursor.close()

#insert menu_item entities
def insert_meal(name, dining_hall, meal):
    query = "insert into menu_item (name) values (%s)"
    args = (name,)

    #retrieve menu_item_ids
    retrieve = "select id from menu_item where name=%s"

    #retrieve current date
    now = datetime.now()
    date = now.strftime('%Y-%m-%d')

    cursor = connection.cursor()
    cursor.execute(query,args) #insert into menu_item

    cursor.execute(retrieve,args) #retrieve menu_item_id
    item_id = cursor.fetchall()
    serves_table(item_id[0][0], dining_hall, meal, date) #link menu_item_id with dining_hall in serves relation

    connection.commit()
    cursor.close()

#insert dining_hall entities
def insert_hours(name, breakfast, lunch, dinner, brunch):
    query_empty = "insert into dining_hall (name, breakfast, lunch, dinner, brunch) values (%s,%s,%s,%s,%s)"
    query_full =  "update dining_hall set breakfast=%s,lunch=%s,dinner=%s,brunch=%s where name=%s"
    query_check = "select count(*) from dining_hall"
    args_empty = (name, breakfast, lunch, dinner, brunch)
    args_full = (breakfast, lunch, dinner, brunch, name)

    cursor = connection.cursor()
    cursor.execute(query_check)
    if (cursor.fetchall()[0][0]<2):
        cursor.execute(query_empty,args_empty)
    else:
        cursor.execute(query_full,args_full)

    connection.commit()
    cursor.close()

#write items to databases
def write_to_db(item_list, dining_hall, meal):
    for x in item_list:
        item = x.strip() #removes tabs and newlines
        if (item != ''): #checks for empty inventories
            insert_meal(item, dining_hall, meal)

#get hours
leutBreakfastHours = leutTree.xpath('//section[@data-jump-nav-title="Breakfast"]//div[@class="site-panel__daypart-time"]/text()')
leutBrunchHours = leutTree.xpath('//section[@data-jump-nav-title="Brunch"]//div[@class="site-panel__daypart-time"]/text()')
leutLunchHours = leutTree.xpath('//section[@data-jump-nav-title="Lunch"]//div[@class="site-panel__daypart-time"]/text()')
leutDinnerHours = leutTree.xpath('//section[@data-jump-nav-title="Dinner"]//div[@class="site-panel__daypart-time"]/text()')

fribBreakfastHours = leutTree.xpath('//section[@data-jump-nav-title="Breakfast"]//div[@class="site-panel__daypart-time"]/text()')
fribBrunchHours = leutTree.xpath('//section[@data-jump-nav-title="Brunch"]//div[@class="site-panel__daypart-time"]/text()')
fribLunchHours = leutTree.xpath('//section[@data-jump-nav-title="Lunch"]//div[@class="site-panel__daypart-time"]/text()')
fribDinnerHours = leutTree.xpath('//section[@data-jump-nav-title="Dinner"]//div[@class="site-panel__daypart-time"]/text()')

#get menu items
leutBreakfastItems = leutTree.xpath('//section[@data-jump-nav-title="Breakfast"]//button[@data-js="site-panel__daypart-item-title"]/text()')
leutBrunchItems = leutTree.xpath('//section[@data-jump-nav-title="Brunch"]//button[@data-js="site-panel__daypart-item-title"]/text()')
leutLunchItems = leutTree.xpath('//section[@data-jump-nav-title="Lunch"]//button[@data-js="site-panel__daypart-item-title"]/text()')
leutDinnerItems = leutTree.xpath('//section[@data-jump-nav-title="Dinner"]//button[@data-js="site-panel__daypart-item-title"]/text()')

fribBreakfastItems = leutTree.xpath('//section[@data-jump-nav-title="Breakfast"]//button[@data-js="site-panel__daypart-item-title"]/text()')
fribBrunchItems = leutTree.xpath('//section[@data-jump-nav-title="Brunch"]//button[@data-js="site-panel__daypart-item-title"]/text()')
fribLunchItems = leutTree.xpath('//section[@data-jump-nav-title="Lunch"]//button[@data-js="site-panel__daypart-item-title"]/text()')
fribDinnerItems = leutTree.xpath('//section[@data-jump-nav-title="Dinner"]//button[@data-js="site-panel__daypart-item-title"]/text()')

#write hours to database
if (len(leutBrunchHours) == 0):
    insert_hours("Leutner", leutBreakfastHours[0].__str__(), leutLunchHours[0].__str__(), leutDinnerHours[0].__str__(), None)
    insert_hours("Fribley", fribBreakfastHours[0].__str__(), fribLunchHours[0].__str__(), fribDinnerHours[0].__str__(), None)
else:
    insert_hours("Leutner", None, None, leutDinnerHours[0].__str__(), leutBrunchHours[0].__str__())
    insert_hours("Fribley", None, None, fribDinnerHours[0].__str__(), fribBrunchHours[0].__str__())

#write menu items to database
write_to_db(leutBreakfastItems, "Leutner", "Breakfast")
write_to_db(leutBrunchItems, "Leutner", "Lunch")
write_to_db(leutLunchItems, "Leutner", "Lunch")
write_to_db(leutDinnerItems, "Leutner", "Dinner")

write_to_db(fribBreakfastItems, "Fribley", "Breakfast")
write_to_db(fribBrunchItems, "Fribley", "Lunch")
write_to_db(fribLunchItems, "Fribley", "Lunch")
write_to_db(fribDinnerItems, "Fribley", "Dinner")
