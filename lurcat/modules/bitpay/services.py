from flask import Blueprint, request, flash, url_for, redirect
import os
import requests
from time import sleep

bitpaybp = Blueprint('bitpaybp', __name__, url_prefix='/bitpay')

@bitpaybp.route('/')
def get_button():
    bpid = os.getenv('BITPAY')

    params = {}

    params['currency'] = 'USD'
    params['price'] = '100.00'

    if not bpid:
        flash('BPID not found', 'warning')
        sleep(2)
        return render_template(url_for('frontend.index'))

    r = requests.post('https://bitpay.com/api/invoice', auth=(bpid, ''), verify=True, params=params)
    return r.text