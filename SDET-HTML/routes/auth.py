from flask import Blueprint, request, session, redirect, url_for, render_template
import firebase_admin
from firebase_admin import credentials, auth
import pyrebase
from config import Config

auth_bp = Blueprint('auth', __name__)

firebase = pyrebase.initialize_app(Config.FIREBASE_CONFIG)
auth_firebase = firebase.auth()

if not firebase_admin._apps:
    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth_firebase.sign_in_with_email_and_password(email, password)
            session['user'] = user
            return redirect(url_for('main.dashboard'))
        except:
            return render_template('login.html', error='Invalid email/password')
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth_firebase.create_user_with_email_and_password(email, password)
            session['user'] = user
            return redirect(url_for('main.dashboard'))
        except:
            return render_template('signup.html', error='Unable to create account')
    return render_template('signup.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.login'))