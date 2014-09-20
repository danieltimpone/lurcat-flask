"""
The MIT License (MIT)

Copyright (c) 2011-2014 BitPay

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import time
import json
import base64
from hashlib import sha256
import hmac
import binascii
import urllib2
import urllib
import collections

import os

"""
The MIT License (MIT)

Copyright (c) 2011-2014 BitPay

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

bpOptions = dict()

# Please look carefully through these options and adjust according to your installation.  
# Alternatively, most of these options can be dynamically set upon calling the functions in bp_lib.

# REQUIRED Api key you created at bitpay.com
# example: bpOptions['apiKey'] = 'L21K5IIUG3IN2J3'
bpOptions['apiKey'] = os.getenv('BITPAY')

# whether to verify POS data by hashing above api key.  If set to false, you should
# have some way of verifying that callback data comes from bitpay.com
# note: this option can only be changed here.  It cannot be set dynamically. 
bpOptions['verifyPos'] = True

# email where invoice update notifications should be sent
bpOptions['notificationEmail'] = ''

# url where bit-pay server should send update notifications.  See API doc for more details.
# example: bpOptions['notificationURL'] = 'https://www.example.com/callback/'
bpOptions['notificationURL'] = ''

# url where the customer should be directed to after paying for the order
# example: bpOptions['redirectURL'] = 'https://www.example.com/confirmation/'
bpOptions['redirectURL'] = ''

# This is the currency used for the price setting.  A list of other pricing
# currencies supported is found at bitpay.com
bpOptions['currency'] = 'BTC'

# Indicates whether anything is to be shipped with
# the order (if false, the buyer will be informed that nothing is
# to be shipped)
bpOptions['physical'] = 'true'

# If set to false, then notifications are only
# sent when an invoice is confirmed (according the the
# transactionSpeed setting). If set to true, then a notification
# will be sent on every status change
bpOptions['fullNotifications'] = 'true'

# transaction speed: low/medium/high.   See API docs for more details.
bpOptions['transactionSpeed'] = 'low'

# Logfile for use by the bpLog function.  Note: ensure the web server process has write access
# to this file and/or directory!
bpOptions['logFile'] = '/bplog.txt'

# Change to 'true' if you would like automatic logging of invoices and errors.
# Otherwise you will have to call the bpLog function manually to log any information.
bpOptions['useLogging'] = False


def bpLog(contents):
    """
    Writes contents to a log file specified in the file or, if missing,
    defaults to a standard filename of 'bplog.txt'.

    :param contents: string
    """
    if bpOptions['logFile'] != "":
        file_name = os.path.realpath(__file__) + bpOptions['logFile']
    else:
        # Fallback to using a default logfile name in case the variable is
        # missing or not set.
        file_name = os.path.realpath(__file__) + '/bplog.txt'

    with open(file_name, "a") as log_file:
        log_file.write(time.strftime('%m-%d %H:%M:%S') + ": ")
        log_file.write(json.dumps(contents) + "\n")


def bpCurl(url, api_key, post=False):
    """
    Handles post/get to BitPay via curl.

    :param url: string
    :param api_key: string
    :param post: bool
    :return response
    """
    if url.strip() and api_key.strip():

        cookie_handler = urllib2.HTTPCookieProcessor()
        redirect_handler = urllib2.HTTPRedirectHandler()
        opener = urllib2.build_opener(redirect_handler, cookie_handler)

        uname = base64.b64encode(api_key)

        opener.addheaders = [
            ('Content-Type', 'application/json'),
            ('Authorization', 'Basic ' + uname),
            ('X-BitPay-Plugin-Info', 'pythonlib1.1'),
        ]

        if post:
            response_string = opener.open(url, urllib.urlencode(json.loads(post))).read()
        else:
            response_string = opener.open(url).read()

        try:
            response = json.loads(response_string)
        except ValueError:
            response = {
                "error": response_string
            }
            if bpOptions['useLogging']:
                bpLog('Error: ' + response_string)

        return response
    else:
        return {
            "error": "url or apiKey were blank."
        }


def bpCreateInvoice(order_id, price, pos_data, options=None):
    """
    Creates BitPay invoice via bpCurl.
    :param order_id: string
    :param price: string
    :param pos_data: string
    :param options: dict
    :return response
    """
    # orderId: Used to display an orderID to the buyer. In the account summary view, this value is used to
    # identify a ledger entry if present. Maximum length is 100 characters.
    #
    # price: by default, price is expressed in the currency you set in   The currency can be
    # changed in options.
    #
    # posData: this field is included in status updates or requests to get an invoice.  It is intended to be used by
    # the merchant to uniquely identify an order associated with an invoice in their system.  Aside from that, Bit-Pay does
    # not use the data in this field.  The data in this field can be anything that is meaningful to the merchant.
    # Maximum length is 100 characters.
    #
    # Note:  Using the posData hash option will APPEND the hash to the posData field and could push you over the 100
    # character limit.
    #
    #
    # options keys can include any of:
    # 'itemDesc', 'itemCode', 'notificationEmail', 'notificationURL', 'redirectURL', 'apiKey'
    # 'currency', 'physical', 'fullNotifications', 'transactionSpeed', 'buyerName',
    # 'buyerAddress1', 'buyerAddress2', 'buyerCity', 'buyerState', 'buyerZip', 'buyerEmail', 'buyerPhone'
    #
    # If a given option is not provided here, the value of that option will default to what is found in bp_options
    # (see api documentation for information on these options).

    if not options:
        options = dict()

    options = dict(bpOptions.items() + options.items())  # options override any options found in bp_options
    pos = {
        "posData": pos_data
    }

    if bpOptions['verifyPos']:
        pos['hash'] = bpHash(str(sanitize_dict(pos_data)), options['apiKey'])

    options['posData'] = json.dumps(pos)

    if len(options['posData']) > 100:
        return {
            "error": "posData > 100 character limit. Are you using the posData hash?"
        }

    options['orderID'] = order_id
    options['price'] = price

    post_options = ['orderID', 'itemDesc', 'itemCode', 'notificationEmail', 'notificationURL', 'redirectURL',
                    'posData', 'price', 'currency', 'physical', 'fullNotifications', 'transactionSpeed', 'buyerName',
                    'buyerAddress1', 'buyerAddress2', 'buyerCity', 'buyerState', 'buyerZip', 'buyerEmail', 'buyerPhone']

    for o in post_options:
        if o in options:
            pos[o] = options[o]

    pos = json.dumps(pos)

    response = bpCurl('https://bitpay.com/api/invoice/', options['apiKey'], pos)

    if bpOptions['useLogging']:
        bpLog('Create Invoice: ')
        bpLog(pos)
        bpLog('Response: ')
        bpLog(response)

    return response


def bpVerifyNotification(api_key=False, post=None):
    """
    Call from your notification handler to convert _POST data to an object containing invoice data

    :param api_key: bool
    :return dict
    """

    if not api_key:
        api_key = bpOptions['apiKey']

    if not post:
        return 'No post data'

    json_data = json.loads(post)

    if 'posData' not in json_data:
        return 'no posData'

    pos_data = json.loads(json_data['posData'])

    if bpOptions['verifyPos'] and pos_data['hash'] != bpHash(str(sanitize_dict(pos_data['posData'])), api_key):
        return 'authentication failed (bad hash)'

    json_data['posData'] = pos_data['posData']

    return json_data


def sanitize_dict(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(sanitize_dict, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(sanitize_dict, data))
    else:
        return data


def bpGetInvoice(invoice_id, api_key=False):
    """
    Retrieves an invoice from BitPay.  options can include 'apiKey'

    :param invoice_id: string
    :param api_key: bool
    :return dict
    """

    if not api_key:
        api_key = bpOptions['apiKey']

    response = bpCurl('https://bitpay.com/api/invoice/' + invoice_id, api_key)

    response['posData'] = json.loads(response['posData'])
    response['posData'] = response['posData']['posData']

    return response


def bpHash(data, key):
    """
    Generates a base64 encoded keyed hash.

    :param data: string
    :param key: string
    :return string
    """

    hashed = hmac.new(key, data, sha256)
    return binascii.b2a_base64(hashed.digest())[:-1]


def bpDecodeResponse(response):
    """
    Decodes JSON response and returns
    associative array.

    :param response: string
    :return dict
    """

    if not response:
        return 'Error: decodeResponse expects a string parameter.'

    return json.loads(response)