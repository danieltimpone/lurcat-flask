# -*- coding: utf-8 -*-
import os
import hashlib
from datetime import datetime
from flask import current_app
from flask.ext.wtf import Form
from flask.ext.wtf.html5 import URLField, EmailField, TelField
from wtforms import (ValidationError, TextField, HiddenField, PasswordField,
    SubmitField, TextAreaField, IntegerField, RadioField,FileField,
    DecimalField, SelectField, DateField, Field, widgets)
from wtforms.validators import (Required, Length, EqualTo, Email, NumberRange, AnyOf, Optional, URL)
from flask.ext.babel import lazy_gettext as _
from flask.ext.login import current_user

from ..user import User
from ..utils import PASSWORD_LEN_MIN, PASSWORD_LEN_MAX, AGE_MIN, AGE_MAX, DEPOSIT_MIN, DEPOSIT_MAX
from ..utils import allowed_file, ALLOWED_AVATAR_EXTENSIONS, make_dir
from ..utils import SEX_TYPE
from ..extensions import db


class ProfileForm(Form):
    multipart = True
    next = HiddenField()
    email = EmailField(_('Email'), [Required(), Email()])
    # Don't use the same name as model because we are going to use populate_obj().
    avatar_file = FileField(_("Avatar"), [Optional()])
    sex_code = RadioField(_("Sex"), [AnyOf([str(val) for val in SEX_TYPE.keys()])], choices=[(str(val), label) for val, label in SEX_TYPE.items()])
    age = IntegerField(_('Age'), [Optional(), NumberRange(AGE_MIN, AGE_MAX)])
    phone = TelField(_('Phone'), [Length(max=64)])
    url = URLField(_('URL'), [Optional(), URL()])
    deposit = DecimalField(_('Deposit'), [Optional(), NumberRange(DEPOSIT_MIN, DEPOSIT_MAX)])
    location = TextField(_('Location'), [Length(max=64)])
    bio = TextAreaField(_('Bio'), [Length(max=1024)])
    submit = SubmitField(_('Save'))

    def validate_name(form, field):
        user = User.get_by_id(current_user.id)
        if not user.check_name(field.data):
            raise ValidationError(_("Please pick another name."))

    def validate_avatar_file(form, field):
        if field.data and not allowed_file(field.data.filename):
            raise ValidationError(_("Please upload files with extensions:")+" %s" % "/".join(ALLOWED_AVATAR_EXTENSIONS))

    def create_profile(self,request,user):

        if self.avatar_file.data:
            upload_file = request.files[self.avatar_file.name]
            if upload_file and allowed_file(upload_file.filename):
                # Don't trust any input, we use a random string as filename.
                # or use secure_filename:
                # http://flask.pocoo.org/docs/patterns/fileuploads/

                user_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], "user_%s" % user.id)
                current_app.logger.debug(user_upload_dir)

                make_dir(user_upload_dir)
                root, ext = os.path.splitext(upload_file.filename)
                today = datetime.now().strftime('_%Y-%m-%d')
                # Hash file content as filename.
                hash_filename = hashlib.sha1(upload_file.read()).hexdigest() + "_" + today + ext
                user.avatar = hash_filename

                avatar_ab_path = os.path.join(user_upload_dir, user.avatar)
                # Reset file curso since we used read()
                upload_file.seek(0)
                upload_file.save(avatar_ab_path)

        self.populate_obj(user)
        self.populate_obj(user.user_detail)

        db.session.add(user)
        db.session.commit()


class PasswordForm(Form):
    next = HiddenField()
    password = PasswordField(_('Current password'), [Required()])
    new_password = PasswordField(_('New password'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    password_again = PasswordField(_('Password again'), [Required(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX), EqualTo('new_password')])
    submit = SubmitField(_('Save'))

    def validate_password(form, field):
        user = User.get_by_id(current_user.id)
        if not user.check_password(field.data):
            raise ValidationError(_("Password is wrong."))

    def update_password(self,user):
        self.populate_obj(user)
        user.password = self.new_password.data

        db.session.add(user)
        db.session.commit()
