# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, flash, current_app, send_from_directory, redirect, url_for
from flask.ext.login import login_required
from flask.ext.babel import Babel
from ..decorators import admin_required

from ..user import User
from .forms import UserForm, EditTranslationForm, UploadLogoForm

from werkzeug import secure_filename

admin = Blueprint('admin', __name__, url_prefix='/admin')
import os

@admin.route('/')
@login_required
@admin_required
def index():
    users = User.query.all()
    logo_form = UploadLogoForm()
    return render_template('admin/index.html', users=users, active='index',logo_form=logo_form)


@admin.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users, active='users')


@admin.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    form = UserForm(obj=user, next=request.args.get('next'))

    if form.validate_on_submit():
        form.save(user)

        flash('User updated.', 'success')

    return render_template('admin/user.html', user=user, form=form)


@admin.route('/translation/edit/<language>', methods=['POST','GET'])
@login_required
@admin_required
def edit_translation(language):
    form = EditTranslationForm(language = language)
    if form.validate_on_submit():
        file = request.files[form.file.name]
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['TRANSLATIONS_FOLDER'], language,current_app.config['TRANSLATIONS_PATH'],current_app.config['TRANSALTIONS_FILE']))
            os.system("pybabel compile -f -d fbone/translations")
            flash("Translation File has been uploaded")
            return redirect(url_for('admin.edit_translation',language=language))
    return render_template('admin/translation.html',form=form)

@admin.route('/translations', methods=['GET'])
@login_required
@admin_required
def translations():
    babel  = Babel(current_app)
    languages = babel.list_translations()
    return render_template('admin/translations.html',languages = languages)

@admin.route('/translation/<language>', methods=['GET'])
@login_required
@admin_required
def existing_translation(language):
    return send_from_directory(os.path.join(current_app.config['TRANSLATIONS_FOLDER'],language,current_app.config['TRANSLATIONS_PATH']),current_app.config['TRANSALTIONS_FILE'])


@admin.route('/logo', methods=['POST'])
@login_required
@admin_required
def upload_logo():
    form = UploadLogoForm()
    if form.validate_on_submit():
        file = request.files[form.file.name]
        if file:
            filename = secure_filename(file.filename)
            file.save(current_app.config['LOGO_FILE'])
            flash("Logo File has been uploaded")
            return redirect(url_for('admin.index'))



