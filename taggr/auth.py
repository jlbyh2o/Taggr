import functools

import subprocess

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from taggr.db import get_db
from taggr.forms import RegisterForm, LoginForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    db = get_db()
    if db.execute('SELECT id FROM user WHERE 1').fetchone() is not None:
        flash('Registration Denied. Only One User Account Allowed.')
        return redirect(url_for('auth.login'))
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = request.form['username']
            password = request.form['password']
            error = None

            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'
            elif db.execute(
                    'SELECT id FROM user WHERE username = ?', (username,)
            ).fetchone() is not None:
                error = f"User {username} is already registered."

            if error is None:
                db.execute(
                    'INSERT INTO user (username, password) VALUES (?, ?)',
                    (username, generate_password_hash(password))
                )
                db.commit()
                flash('User Registered Successfully.')
                return redirect(url_for('auth.login'))

            flash(error)
    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = request.form['username']
            password = request.form['password']
            db = get_db()
            error = None
            user = db.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()

            if user is None:
                error = 'Incorrect username.'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'

            if error is None:
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('index'))

            flash(error)

    return render_template('auth/login.html', form=form)


@bp.route('/settings', methods=('GET', 'POST'))
def settings():
    if g.user is None:
        return redirect(url_for('auth.login'))

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

    if request.method == 'POST':
        square_api_key = request.form['squareApiKey']
        dymo_printer_name = request.form['dymoPrinterName']
        if dymo_printer_name not in printers:
            error = "Printer name is invalid. Printer Could Not Be Set."
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE user SET square_api_key = ?, dymo_printer_name = ? WHERE id = ?',
                (square_api_key, dymo_printer_name, g.user['id'],)
            )
            db.commit()
            flash("Settings Updated Successfully.")
        return redirect(url_for('auth.settings'))

    return render_template('auth/settings.html', printers=printers)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
