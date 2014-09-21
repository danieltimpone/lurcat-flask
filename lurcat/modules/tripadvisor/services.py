from flask import Blueprint, render_template, request, flash, url_for, redirect
import json, os
import requests

tripadvisorbp = Blueprint('tripadvisorbp', __name__, url_prefix='/tripadvisor')

@tripadvisorbp.route('/')
def get_hotels(city='atlanta'):
	params = {}
	auth_key = os.getenv('TRIPADVISOR')

	params['format'] = 'json'
	request.args.get('city')

	if not city:
		city = 'atlanta'

	r = requests.get('http://api.tripadvisor.com/api/partner/1.0/search/' + city + '?key=' + auth_key)
	jDict = json.loads(r.text)
	hDict = jDict['hotels']


	return render_template('tripadvisor/hotels.html', jDict=jDict, city=city)

	

	

