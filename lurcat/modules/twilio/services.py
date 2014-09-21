import os, twilio, json
from twilio.rest import TwilioRestClient
from flask import Blueprint, render_template, jsonify, request

twiliobp = Blueprint('twilio', __name__, url_prefix='/twilio')
site_number = "+12676425048"

@twiliobp.route('/home')
def home():
    return render_template('twilio/home.html')


@twiliobp.route('/send_message', methods=['GET', 'POST'])
def send_message():
		data = json.loads(request.data)
		account_sid = 'AC7c69a4ecb0dc9eab5677c59624253c7f' 
		auth_token = os.getenv('TWILIO')
		client = twilio.rest.TwilioRestClient(account_sid, auth_token) 
		print data
		sms = client.sms.messages.create(body=data['text-message'],
		to=data['recipient'],from_=site_number)
		return jsonify({'key': data})


    


    

