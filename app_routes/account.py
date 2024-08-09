from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from ..models import User, Organisation
from werkzeug.security import generate_password_hash, check_password_hash
from ..init_extensions import db, login_manager, mail, bcrypt
from .email_util import send_email
from datetime import datetime
from ..Server_Side_Processing.verify_paseto import generate_paseto_token, verify_paseto_token, resend_verification_email

account_bp = Blueprint('account', __name__)

@account_bp.route('/')
def login():
    organisations = Organisation.query.all()
    users = User.query.all()
    return render_template('login.html', title='Login', organisations=organisations, users=users)

# Organisation Login Route
@account_bp.route('/login_organisation', methods=['GET', 'POST'])
def login_organisation():
    if request.method == 'POST':
        organisation_id = request.form.get('organisation')
        password = request.form.get('password')
        organisation = Organisation.query.get(organisation_id)
        
        if organisation and bcrypt.check_password_hash(organisation.password, password):
            login_user(organisation, remember=True)
            return redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check password', 'danger')
    organisations = Organisation.query.all()
    return render_template('login.html', organisations=organisations)

# Employee Login Route
@account_bp.route('/login_employee', methods=['GET', 'POST'])
def login_employee():
    if request.method == 'POST':
        organisation_id = request.form.get('organisation')
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, organisation_id=organisation_id).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            if user.verified:
                login_user(user, remember=True)
                return redirect(url_for('main.index'))
            else:
                return redirect(url_for('account.verify_account', email=user.email, username=user.username))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    organisations = Organisation.query.all()
    return render_template('login.html', organisations=organisations)

# Guest Login Route
@account_bp.route('/guest')
def guest():
    return render_template('index.html')

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

@account_bp.route('/register_organisation', methods=['GET', 'POST'])
def register_organisation():
    if request.method == 'POST':
        organisation_name = request.form.get('organisation_name')
        organisationEmail = request.form.get('email')
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
    email = request.form.get('email')
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

@account_bp.route('/resend_verification', methods=['POST'])
def resend_verification():
    email = request.form['email']
    account_type = request.form['account_type']
    resend_verification_email(email, account_type)
    flash('A new verification email has been sent.', 'info')
    return redirect(url_for('main.verify_account', email=email, account_type=account_type))