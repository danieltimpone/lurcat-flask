import os, twilio
from twilio.rest import TwilioRestClient
from flask import Blueprint

twiliobp = Blueprint('twilio', __name__, url_prefix='/twilio')

def send_message(client):
    sms = client.sms.messages.create(body="All in the game, yo",
    to="+17274090736",from_="+15005550006")
    return sms


@twiliobp.route('/')
def index():
    account_sid = 'AC7c69a4ecb0dc9eab5677c59624253c7f' 
    auth_token = os.getenv('TWILIO')
    client = twilio.rest.TwilioRestClient(account_sid, auth_token)
    try:
        send_message(client)
    except twilio.rest.exceptions.TwilioRestException as e:
        return 'bummer nerd'
    


    

