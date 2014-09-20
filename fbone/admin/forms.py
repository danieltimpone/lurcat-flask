# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from flask.ext.wtf.html5 import URLField, EmailField, TelField
from wtforms import (ValidationError, TextField, HiddenField, PasswordField,
    SubmitField, TextAreaField, IntegerField, RadioField,FileField,
    DecimalField, SelectField, DateField, Field, widgets)
from wtforms.validators import (Required, Length, EqualTo, Email, NumberRange, AnyOf, Optional, URL)
from ..extensions import db

from ..user import USER_ROLE, USER_STATUS


class UserForm(Form):
    next = HiddenField()
    role_code = RadioField(u"Role", [AnyOf([str(val) for val in USER_ROLE.keys()])],
            choices=[(str(val), label) for val, label in USER_ROLE.items()])
    status_code = RadioField(u"Status", [AnyOf([str(val) for val in USER_STATUS.keys()])],
            choices=[(str(val), label) for val, label in USER_STATUS.items()])
    # A demo of datepicker.
    created_time = DateField(u'Created time')
    submit = SubmitField(u'Save')

    def save(self,user):
        self.populate_obj(user)
        db.session.add(user)
        db.session.commit()


class EditTranslationForm(Form):
    multipart = True
    file = FileField(u"Upload Translation File")
    language = HiddenField()
    submit = SubmitField(u'Save')


class UploadLogoForm(Form):
    multipart = True
    file = FileField(u"Upload Logo File")
    submit = SubmitField(u'Save')