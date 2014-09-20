# -*- coding: utf-8 -*-

import requests, datetime, json
import os
from flask import Blueprint, request, jsonify
import mailchimp

mailchimpbp = Blueprint('mailchimp', __name__, url_prefix='/mailchimp')
base = 'http://taxee.io/api/v1/'
year = str(datetime.datetime.now().year)

def get_mailchimp_api():
    return mailchimp.Mailchimp(os.getenv('MAILCHIMP'))

@mailchimpbp.route('/')
def index():
    m = get_mailchimp_api()
    try:
        m.helper.ping()
    except mailchimp.Error:
        return "Invalid API key"

    return "HERE"