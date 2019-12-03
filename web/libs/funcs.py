from flask import request
from datetime import datetime

'''
Created on Nov 30, 2019

@author: Jacob
'''

def date_from_request():
    date = datetime.today().date()
    if "date" in request.args:
        try:
            date = datetime.strptime(request.args["date"], "%Y-%m-%d").date()
        except ValueError:
            None
            
    return date