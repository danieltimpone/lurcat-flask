from flask import Blueprint, render_template, request, flash, url_for, redirect
import json
import requests

yahooweatherbp = Blueprint('yahooweatherbp', __name__, url_prefix='/yweather')

@yahooweatherbp.route('/forecast/')
def forecast(city='Atlanta', state='ga'):
    params_dict = {}

    params_dict['format'] = 'json'
    # city, state
    city = request.args.get('city')
    state = request.args.get('state')

    if not city or not state:
        city = 'Atlanta'
        state = 'ga'

    params_dict['q'] = ('select * from weather.forecast ' +
                        'where woeid in (select woeid from geo.places(1) ' + 
                        'where text="' + city + ', ' + state + '")')


    params_dict['env'] = 'store://datatables.org/Falltableswithkeys'

    r = requests.get("https://query.yahooapis.com/v1/public/yql", params=params_dict)
    jdict = json.loads(r.text)


    wxDict = jdict['query']['results']['channel']['item']

    return render_template('yahooweather/forecast.html', city=city, state=state, wxDict=wxDict)