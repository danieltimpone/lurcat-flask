from flask import Blueprint, request, flash, url_for, redirect, render_template, jsonify
import os
import json
import requests
from time import sleep
import bp_lib

bitpaybp = Blueprint('bitpaybp', __name__, url_prefix='/bitpay')

@bitpaybp.route('/')
def get_button():
    return render_template('bitpay/bitpay.html')

@bitpaybp.route('/donate')
def donate():
    return render_template('bitpay/donate.html')

@bitpaybp.route('/buy_hampster', methods=['GET', 'POST'])
def buy_hampster():
    bp_lib.bpOptions['api_key'] = os.getenv('BITPAY')
    data = json.loads(request.data)
    
    response = bp_lib.bpCreateInvoice('1', '0.0001', '123123', options=data)
    return jsonify({'key': response})

