import subprocess

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from flask_login import current_user, login_user, logout_user, login_required
from taggr.models import User
from taggr import db
from taggr.forms import RegisterForm, LoginForm, SettingsForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if User.query.all() is not None:
        flash('Registration Denied. Only One User Account Allowed.')
        return redirect(url_for('auth.login'))
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('auth/login.html', form=form)


@bp.route('/settings', methods=('GET', 'POST'))
@login_required
def settings():
    # Get Printers from System
    printers = subprocess.check_output(['lpstat', '-e']).decode('utf-8')
    printers = printers.split('\n')
    if len(printers) == 0:
        printers = ['No Printers Found']
    elif len(printers) == 1:
        if printers[0] is None:
            printers = ['No Printers Found']
    if len(printers) > 1:
        printers = list(filter(None, printers))

    form = SettingsForm()
    if form.validate_on_submit():
        square_api_key = form.square_api_key.data
        dymo_printer_name = form.dymo_printer_name.data
        if dymo_printer_name not in printers:
            error = "Printer name is invalid. Printer Could Not Be Set."
            flash(error)
        else:
            current_user.square_api_key = square_api_key
            current_user.dymo_printer_name = dymo_printer_name
            db.session.commit()
            flash("Settings Updated Successfully.")
        return redirect(url_for('auth.settings'))

    return render_template('auth/settings.html', printers=printers, form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
