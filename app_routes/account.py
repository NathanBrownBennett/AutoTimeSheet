from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from ..models import User, Organisation
from werkzeug.security import generate_password_hash, check_password_hash
from ..init_extensions import db, login_manager, mail, bcrypt
from .email_util import send_email
from datetime import datetime

account_bp = Blueprint('account', __name__)

@account_bp.route('/')
def login():
    if request.method == 'POST':
        organisation_id = request.form.get('organisation')
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, organisation_id=organisation_id).first()
        if user and user.check_password(password):
            login_user(user)
            send_email(user.email, 'Login Alert', f'You have logged in from a device at {datetime.now()}.')
            return redirect(url_for('main.index'))
        flash('Login Unsuccessful. Please check username and password', 'danger')
    organisations = Organisation.query.all()
    return render_template('login.html', title='Login', organisations=organisations)

@account_bp.route('/account_settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    if request.method == 'POST':
        return render_template('account_settings.html', title='Account Settings', user=current_user, role=current_user.role)
        pass
    return render_template('account_settings.html')

@account_bp.route('/login', methods=['GET', 'POST'])
def check_login():
    if current_user.is_authenticated:
        if current_user.is_verified:
            return redirect(url_for('main.index'))
        if not current_user.is_verified:
            return redirect(url_for('account.verify_account'))
    else:
        return redirect(url_for('account.login'))

@account_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@account_bp.route('/register', methods=['GET', 'POST'])
def register_organisation():
    if request.method == 'POST':
        organisation_name = request.form.get('organisation_name')
        username = request.form.get('username')
        password = request.form.get('password')
        organisation = Organisation.query.filter_by(name=organisation_name).first()
        if not organisation:
            organisation = Organisation(name=organisation_name)
            db.session.add(organisation)
            db.session.commit()
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password_hash=hashed_password, organisation_id=organisation.id)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        send_email(new_user.email, 'Welcome!', 'Your account has been created.')
        send_email(organisation.email, 'New User', f'A new user has been added to your organisation: {new_user.username}')
        return redirect(url_for('account.login'))
    return render_template('register.html')

@account_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    db.session.delete(user)
    db.session.commit()
    flash('Account deleted successfully.', 'success')
    return redirect(url_for('account.login'))

@account_bp.route('/verify_account', methods=['POST'])
def verify_account():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        user.is_verified = True
        if user.number_of_logins == 0:
            user.last_login_time = datetime.now()
            return render_template('verify_account.html', user=user, title='Verify Account - Change Password')
        db.session.commit()
        flash('Account verified successfully.', 'success')
        return redirect(url_for('main.index'))
    else:
        flash('Invalid username or password.', 'danger')
    return redirect(url_for('account.login'))
