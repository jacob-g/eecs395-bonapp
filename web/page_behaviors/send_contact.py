from libs.db import DBConnector
from flask import abort, redirect, request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

type = "action"

contact_email = "maintenance@case.edu"

def send_email(from_address, subject, message):
    user = "bonappalerts@gmail.com"
    pwd = "BonAppAlerts1"

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = contact_email
    msg['Subject'] = "Bon-App Contact: " + subject

    body = message
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(user, pwd)
    text = msg.as_string()
    server.sendmail(user, contact_email, text)
    server.close()

def preempt(db : DBConnector, metadata : dict):
    if metadata["login_state"].user is None or "title" not in request.form or "comment" not in request.form:
        return abort(404)
    
def action(db : DBConnector, metadata : dict):
    send_email(metadata["login_state"].user.user_id + "@case.edu", request.form["title"], request.form["comment"])
    return redirect("/contact?sent")