import lxml.html
import requests
import mysql.connector

#retrieve web page data
leutPage = requests.get("https://case.cafebonappetit.com/cafe/leutner-cafe/")
fribPage = requests.get("https://case.cafebonappetit.com/cafe/fribley-marche/")

#save html file
leutTree = lxml.html.fromstring(leutPage.content)
fribTree = lxml.html.fromstring(fribPage.content)

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

#connect to database
connection = mysql.connector.connect(host="localhost", user="bonapp", password="password", database="review")

def insert_meal(name, dining_hall, meal):
    query = "insert into menu_item (name, dining_hall,meal) values (%s, %s, %s)"
    args = (name, dining_hall, meal)

    cursor = connection.cursor()
    cursor.execute(query,args)

    connection.commit()
    cursor.close()

#write items to database
for x in leutBreakfastItems:
    item = x.strip() #removes tabs and newlines
    if (item != ''): #checks for empty entries
        insert_meal(item, "Leutner", "Breakfast")

for x in leutBrunchItems:
    item = x.strip() #removes tabs and newlines
    if (item != ''): #checks for empty entries
        insert_meal(item, "Leutner", "Brunch")

for x in leutLunchItems:
    item = x.strip() #removes tabs and newlines
    if (item != ''): #checks for empty entries
        insert_meal(item, "Leutner", "Lunch")

for x in leutDinnerItems:
    item = x.strip() #removes tabs and newlines
    if (item != ''): #checks for empty entries
        insert_meal(item, "Leutner", "Dinner")

for x in fribBreakfastItems:
    item = x.strip() #removes tabs and newlines
    if (item != ''): #checks for empty entries
        insert_meal(item, "Fribley", "Breakfast")

for x in fribBrunchItems:
    item = x.strip() #removes tabs and newlines
    if (item != ''): #checks for empty entries
        insert_meal(item, "Fribley", "Brunch")

for x in fribLunchItems:
    item = x.strip() #removes tabs and newlines
    if (item != ''): #checks for empty entries
        insert_meal(item, "Fribley", "Lunch")

for x in fribDinnerItems:
    item = x.strip() #removes tabs and newlines
    if (item != ''): #checks for empty entries
        insert_meal(item, "Fribley", "Dinner")
