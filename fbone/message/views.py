
# -*- coding: utf-8 -*-

import os

from flask import Blueprint, render_template, send_from_directory, abort, redirect, url_for, request, flash
from flask import current_app as app
from flask.ext.babel import gettext as _

from flask.ext.login import login_required, current_user
from .forms import CreateMessageForm, ResponseMessageForm
from .models import Message, StaredMessages, TimeLine
import json

message = Blueprint('message', __name__, url_prefix='/message')


@message.route('/add_message', methods=['POST'])
@login_required
def add_message():
	user = current_user
	form = CreateMessageForm()
	if form.validate_on_submit():
		form.add_message(user)
		flash(_("Your message has been added"),'success')
	msg = Message()
	return redirect(url_for('user.index'))

@message.route('/add_starred_message/<int:message_id>/<int:offset>', methods=['GET'])
def add_star_message(message_id,offset):
	user = current_user
	star_message = StaredMessages()
	star_message.add(
		user_id = current_user.id,
		message_id = message_id
		)
	timeline = TimeLine()
	timeline.add(current_user.id, message_id, starred = True)
	return redirect(url_for('user.index',offset = offset))

@message.route('/remove_starred_message/<int:message_id>/<int:offset>', methods=['GET'])
def remove_star_message(message_id,offset):
	user = current_user
	star_message = StaredMessages()
	star_message.delete_by_id(message_id)
	return redirect(url_for('user.index',offset = offset))

# Get Next Message to record responses
@message.route('/message_response', methods=['GET'])
@message.route('/message_response/<int:offset>', methods=['GET'])
def message_response(offset=0):
	user = current_user
	msg = Message()
	msg = msg.get_response_message(user,offset)
	print msg
	if(msg is not None):
		form = ResponseMessageForm(offset = offset,message_id = msg.message_id)
	else:
		form = ResponseMessageForm(offset = offset)
	return render_template('user/responses.html', user=user,message = msg,offset=offset,response_form=form)

@message.route('/message_response/<int:parent_id>', methods=['POST'])
def add_message_response(parent_id):
	user = current_user
	form = ResponseMessageForm()
	msg = Message()
	# try:
	form.add_response(user,parent_id)
	# except Exception as e:
	# 	print e
	# 	abort(500,e)
	return redirect(url_for('user.index',offset = 0))

@message.route('/<int:id>', methods=['GET'])
def get(id):
	msg = Message()
	msg = msg.get_by_id(id)
	form = ResponseMessageForm(offset = 0)
	return re



@message.route('/responses/<int:id>', methods=['GET'])
def get_responses(id):
	msg = Message()
	messages =  msg.get_responses(id)
	messages = [{'id':x.message_id,'text':x.text,'response':x.response} for x in messages]
	return json.dumps(messages)

