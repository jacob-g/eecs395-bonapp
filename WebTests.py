import unittest
import lxml.html
import lxml.etree as etree
import urllib.request
#from WebScraper import ______

class WebTests(unittest.TestCase):

    #create mock leutner menupage
    page = open("static_menupage.htm", 'r', encoding='utf-8')
    page_src = page.read()

    #retrieve page data
    testtree = etree.parse(page_src)

    
