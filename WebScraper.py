import lxml.html
import lxml.etree
import requests
import mysql.connector
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

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

#send email alerts if item is available
def send_email(user_email, item_name):

    user = "bonappalerts@gmail.com"
    pwd = "BonAppAlerts1"

    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = user_email + "@case.edu"
    msg['Subject'] = item_name + " is Available Today!"

    body = "You have signed up to receive an email alert when " + item_name + " is available in the dining halls. Enjoy your meal today!"
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(user, pwd)
    text = msg.as_string()
    server.sendmail(user, user_email + "@case.edu", text)
    server.close()

#check for users with active alerts
def alert():
    #retrieve all users and items for which they have alerts
    query_retrieve = "select user, menu_item.name from alert, menu_item where alert.menu_item_id=menu_item.id"
    query_check = "select count(menu_item.id) from menu_item, serves where menu_item.name=%s and menu_item.id=serves.menu_item_id and date(serves.date_of)=date(now())"

    cursor = connection.cursor()
    cursor.execute(query_retrieve) #get all alert data
    alert_data = cursor.fetchall()

    for x in range(len(alert_data)):
        args = (alert_data[x][1],)
        cursor.execute(query_check,args)
        if (cursor.fetchall()[0][0]>0):
            send_email(alert_data[x][0],alert_data[x][1])

    connection.commit()
    cursor.close()

#get hours
leutBreakfastHours = leutTree.xpath('//section[@data-jump-nav-title="Breakfast"]//div[@class="site-panel__daypart-time"]/text()')
leutBrunchHours = leutTree.xpath('//section[@data-jump-nav-title="Brunch"]//div[@class="site-panel__daypart-time"]/text()')
leutLunchHours = leutTree.xpath('//section[@data-jump-nav-title="Lunch"]//div[@class="site-panel__daypart-time"]/text()')
leutDinnerHours = leutTree.xpath('//section[@data-jump-nav-title="Dinner"]//div[@class="site-panel__daypart-time"]/text()')

fribBreakfastHours = fribTree.xpath('//section[@data-jump-nav-title="Breakfast"]//div[@class="site-panel__daypart-time"]/text()')
fribBrunchHours = fribTree.xpath('//section[@data-jump-nav-title="Brunch"]//div[@class="site-panel__daypart-time"]/text()')
fribLunchHours = fribTree.xpath('//section[@data-jump-nav-title="Lunch"]//div[@class="site-panel__daypart-time"]/text()')
fribDinnerHours = fribTree.xpath('//section[@data-jump-nav-title="Dinner"]//div[@class="site-panel__daypart-time"]/text()')

#get menu items
leutBreakfastItems = leutTree.xpath('//section[@data-jump-nav-title="Breakfast"]//button[@data-js="site-panel__daypart-item-title"]/text()')
leutBrunchItems = leutTree.xpath('//section[@data-jump-nav-title="Brunch"]//button[@data-js="site-panel__daypart-item-title"]/text()')
leutLunchItems = leutTree.xpath('//section[@data-jump-nav-title="Lunch"]//button[@data-js="site-panel__daypart-item-title"]/text()')
leutDinnerItems = leutTree.xpath('//section[@data-jump-nav-title="Dinner"]//button[@data-js="site-panel__daypart-item-title"]/text()')

fribBreakfastItems = fribTree.xpath('//section[@data-jump-nav-title="Breakfast"]//button[@data-js="site-panel__daypart-item-title"]/text()')
fribBrunchItems = fribTree.xpath('//section[@data-jump-nav-title="Brunch"]//button[@data-js="site-panel__daypart-item-title"]/text()')
fribLunchItems = fribTree.xpath('//section[@data-jump-nav-title="Lunch"]//button[@data-js="site-panel__daypart-item-title"]/text()')
fribDinnerItems = fribTree.xpath('//section[@data-jump-nav-title="Dinner"]//button[@data-js="site-panel__daypart-item-title"]/text()')

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

#check for alerts
alert()
