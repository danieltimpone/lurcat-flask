# -*- coding: utf-8 -*-

from flask import Markup, current_app

from flask.ext.wtf import Form
from flask.ext.wtf.html5 import URLField, EmailField, TelField
from wtforms import (ValidationError, BooleanField, TextField, HiddenField, PasswordField,
    SubmitField, TextAreaField, IntegerField, RadioField,FileField,
    DecimalField, SelectField, DateField, Field, widgets)
from wtforms.validators import (Required, Length, EqualTo, Email, NumberRange, AnyOf, Optional, URL)
from flask import current_app
from flask.ext.babel import lazy_gettext as _

from ..user import User, UserDetail

from ..user import User
from ..utils import (PASSWORD_LEN_MIN, PASSWORD_LEN_MAX,
        USERNAME_LEN_MIN, USERNAME_LEN_MAX)
from ..extensions import db

class LoginForm(Form):
    next = HiddenField()
    login = TextField(_('Username or email'), [Required()])
    password = PasswordField(_('Password'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    remember = BooleanField(_('Remember me'))
    submit = SubmitField(_('Sign in'))


class SignupForm(Form):
    next = HiddenField()
    email = EmailField(_('Email'), [Required(), Email()],
            description=_("What's your email address?"))
    password = PasswordField(_('Password'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)],
            description=_('%(minChar)s characters or more! Be tricky.', minChar = PASSWORD_LEN_MIN) )
    name = TextField(_('Choose your username'), [Required(), Length(USERNAME_LEN_MIN, USERNAME_LEN_MAX)],
            description=_("Don't worry. you can change it later."))
    agree = BooleanField(_('Agree to the ') +
        Markup('<a target="blank" href="/terms">'+_('Terms of Service')+'</a>'), [Required()])
    submit = SubmitField('Sign up')

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first() is not None:
            raise ValidationError(_('This username is taken'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError(_('This email is taken'))

    def signup(self):
        user = User()
        user.user_detail = UserDetail()
        self.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        return user


class RecoverPasswordForm(Form):
    email = EmailField(_('Your email'), [Email()])
    submit = SubmitField(_('Send instructions'))




class ChangePasswordForm(Form):
    activation_key = HiddenField()
    password = PasswordField(_('Password'), [Required()])
    password_again = PasswordField(_('Password again'), [EqualTo('password', message="Passwords don't match")])
    submit = SubmitField(_('Save'))




class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField(_('Password'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    submit = SubmitField(_('Reauthenticate'))



class OpenIDForm(Form):
    openid = TextField(_('Your OpenID'), [Required()])
    submit = SubmitField(_('Log in with OpenID'))

    def login(self,oid):
        openid = self.openid.data
        current_app.logger.debug('login with openid(%s)...' % openid)
        return oid.try_login(openid, ask_for=['email', 'fullname', 'nickname'])


class CreateProfileForm(Form):
    openid = HiddenField()
    name = TextField(_('Choose your username'), [Required(), Length(USERNAME_LEN_MIN, USERNAME_LEN_MAX)],
            description=_("Don't worry. you can change it later."))
    email = EmailField(_('Email'), [Required(), Email()], description=_("What's your email address?"))
    password = PasswordField(_('Password'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)],
            description=_('%(minChar)s characters or more! Be tricky.',minChar =PASSWORD_LEN_MIN))
    submit = SubmitField(_('Create Profile'))

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first() is not None:
            raise ValidationError(_('This username is taken.'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError(_('This email is taken.'))

    def create_profile(self):
        user = User()
        self.populate_obj(user)
        db.session.add(user)
        db.session.commit()
