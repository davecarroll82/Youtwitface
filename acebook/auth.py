import functools
import os
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Flask
)
from werkzeug.security import check_password_hash, generate_password_hash

from acebook.db import get_db
from acebook.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')
app = Flask(__name__, instance_relative_config=True)

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        photo = request.files['file']
        profile_picture_path = os.path.join("/Users/kyrsten/Projects/Python_Stuff/YouTwitFace/acebook-flask-template/acebook/static/images",secure_filename(photo.filename))
        photo.save(profile_picture_path)
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif User.find(username) is not None:
            error = f"User {username} is already registered."

        if error is None:
            User.create(username, password, secure_filename(photo.filename), )
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None
        user = User.find(username)

        if user is None:
            error = 'Incorrect username.'
        elif not user.authenticate(password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.find_by_id(user_id)

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