# -*- coding: utf-8 -*-

import os

from flask import Blueprint, render_template, send_from_directory, abort, redirect, url_for, request, flash
from flask import current_app as APP
from flask.ext.babel import gettext as _
from flask.ext.login import login_required, current_user
from fbone.message.forms import CreateMessageForm, ResponseMessageForm
from fbone.message.models import Message
from .models import User


user = Blueprint('user', __name__, url_prefix='/user')



@user.route('/')
@user.route('/<int:offset>')
@login_required
def index(offset = 0):
    if not current_user.is_authenticated():
        abort(403)
    create_form = CreateMessageForm()
    message = Message()
    messages = message.get_all_messages()
    msgs = Message()
    msgs = msgs.get_messages_feed(current_user)
    print "test:"
    print msgs
    form = ResponseMessageForm(offset = offset,yes='1',no='2')
    return render_template('user/index.html', user=current_user,form=create_form,response_form = form,messages=msgs,offset=offset)



@user.route('/<int:user_id>/profile')
def profile(user_id):
    user = User.get_by_id(user_id)
    message = Message()
    msgs = message.get_message_from_user(user)
    return render_template('user/profile.html', user=user,messages= msgs,current_user=current_user,followed = current_user.is_following(user))


@user.route('/<int:user_id>/avatar/<path:filename>')
@login_required
def avatar(user_id, filename):
    dir_path = os.path.join(APP.config['UPLOAD_FOLDER'], 'user_%s' % user_id)
    return send_from_directory(dir_path, filename, as_attachment=True)


@user.route('/follow_user/<int:user_id>')
@login_required
def follow_user(user_id):
    user = User.get_by_id(user_id)
    current_user.follow(user)
    flash(_("You are now following") +" %s"%user.name,'success')
    return render_template('user/profile.html', user=user,current_user=current_user,followed = current_user.is_following(user))

@user.route('/unfollow_user/<int:user_id>')
@login_required
def unfollow_user(user_id):
    user = User.get_by_id(user_id)
    current_user.unfollow(user)
    flash(_("You are now not following")+" %s"%user.name,'success')
    return render_template('user/profile.html', user=user,current_user=current_user,followed = current_user.is_following(user))



