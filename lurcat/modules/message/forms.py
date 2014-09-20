# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from flask.ext.babel import lazy_gettext as _
from wtforms import (TextField, HiddenField, SubmitField)
from wtforms.validators import Required

from lurcat.addons.extensions import db
from .models import Message, TimeLine


class CreateMessageForm(Form):
    text = TextField(_('What\'s on your mind'), [Required()],
            description=_("Post will appear on your time line"))
    submit = SubmitField(_('Share'))

    def add_message(self,user):
    	self.populate_obj(user)
    	message = Message()
        message.text = self.text.data
        message.user_id = user.id


        db.session.add(message)
        db.session.commit()


class ResponseMessageForm(Form):
    message_id = HiddenField()
    offset = HiddenField()
    comment = TextField(_("Comment"),description=_("What do you have to say about this post"))
    yes = SubmitField(_('Yes'))
    no = SubmitField(_('No'))

    def add_response(self,user,parent_id):
        self.populate_obj(user)
        comment = self.comment.data
        resp = self.yes.data
        resp = None if resp == "None" else resp
        if resp:
            timeline = TimeLine()
            timeline.add(user.id, parent_id, agreed = True)

        if(comment == '' and resp == None):
    		return False
        parent = Message()
        parent = parent.get_by_id(parent_id)
        response = Message()
        response.root_id = parent_id if parent.root_id is None else parent_id.root_id
        response.user_id = user.id
        response.parent_id = parent_id
        response.text = comment
        response.response = resp
        response.save()
        parent.last_activity = response.last_activity
        parent.save()
        return True
