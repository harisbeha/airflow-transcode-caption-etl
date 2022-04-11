# encoding: utf-8
from __future__ import unicode_literals

import logging

from django.conf import settings
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

logger = logging.getLogger(__name__)

def get_sendgrid_client():
    sg_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
    return sg_client

def send_email_async(to_targets="", subject="MyApp by MyDomain", content="Notification from Cirrus"):
    from_email = Email("cirrus@mydomain.com")
    to_email = Email([to_targets])
    subject = subject
    content = Content("text/html", content)
    mail = Mail(from_email, subject, to_email, content)
    # Now, send the message asynchronously
    sg = get_sendgrid_client()
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response)

def send_order_started_email(user, order_items):
    to_email = user.email
    title = "MyApp by MyDomain - Processing Started"
    
    job_list = ""
    job_list += "</br> <ul>"
    job_list_end = "</ul>"
    for item in order_items:
        formatted_string = "<li>{0}</li>".format(item.entry.title)
        job_list += formatted_string
    message = "Processing started: </br>" + job_list + job_list_end
    send_email_async(to_targets=to_email, subject=title, content=message)
