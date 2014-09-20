# -*- coding: utf-8 -*-
import os
from time import sleep
from flask import Blueprint, render_template, request, flash, url_for, redirect
import mailchimp


def get_mailchimp_api():
    mc = mailchimp.Mailchimp(os.getenv('MAILCHIMP'))
    return mc

mailchimpbp = Blueprint('mailchimpbp', __name__, url_prefix='/mailchimp')

@mailchimpbp.route('/test')
def index():
    m = get_mailchimp_api()
    try:
        m.helper.ping()
    except mailchimp.Error:
        return "Invalid API key"
    return render_template('mailchimp/home.html')
    

@mailchimpbp.route('/subscribe/')
def subscribe(list_id=None):
    email = request.args.get('email')
    list_id = request.args.get('list_id')

    try:
        m = get_mailchimp_api()
        if not list_id:
            lists = m.lists.list()
            if lists:
              list_id = lists['data'][0]['id']
        m.lists.subscribe(list_id, {'email':email})
        flash("The email has been successfully subscribed", 'warning')
    except mailchimp.ListAlreadySubscribedError:
        flash("That email is already subscribed to the list", 'warning')
        sleep(2)
    except mailchimp.Error, e:
        flash('An error occurred: %s - %s' % (e.__class__, e), 'warning')
        sleep(2)
    return redirect( url_for('mailchimpbp.index') )

@mailchimpbp.route('/show_all_lists/')
def show_all_lists():
    try:
        m = get_mailchimp_api()
        lists = m.lists.list()
    except mailchimp.Error, e:
        flash('An error occurred: %s - %s' % (e.__class__, e), 'warning')
        sleep(1)
    return render_template('mailchimp/showlists.html', lists=lists) #whhaaaaaaa)




