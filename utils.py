# utils.py
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import session, redirect, url_for
from models import User

def hash_password(password):
    return generate_password_hash(password)

def check_password(plain_password, hashed_password):
    return check_password_hash(hashed_password, plain_password)

def get_current_user():
    if 'user_id' in session:
        try:
            return User.get_by_id(session['user_id'])
        except:
            return None
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
