import os
from twilio.rest import TwilioRestClient
from flask import Blueprint

twiliobp = Blueprint('twilio', __name__, url_prefix='/twilio')

@twiliobp.route('/')
def index():
	account = "AC7c69a4ecb0dc9eab5677c59624253c7f" 

	token = os.getenv("TWILIO")

	client = TwilioRestClient(account, token)
