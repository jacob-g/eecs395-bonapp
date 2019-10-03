from lxml import html
from lxml import cssselect
from lxml.cssselect import CSSSelector
import requests

#retrieve web page data
leutnerPage = requests.get("https://case.cafebonappetit.com/cafe/leutner-cafe/")

#save html file
leutnerTree = html.fromstring(leutnerPage.content)

#get breakfast
leutnerBreakfast = leutnerTree.cssselect('.site-panel__daypart-time')
print(leutnerBreakfast[1])
