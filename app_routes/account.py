from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from ..models import User, Organisation
from werkzeug.security import generate_password_hash, check_password_hash
from ..init_extensions import db, login_manager, mail, bcrypt
from .email_util import send_email, resend_verification_email, send_verification_email, send_update_email, send_confirmation_email
from datetime import datetime
from ..Server_Side_Processing.verify_paseto import verify_code, generate_code
from ..forms import RegistrationForm

account_bp = Blueprint('account', __name__)

types_of_accounts = [Organisation, User, 'employee', 'guest', 'admin']

ACCOUNT_TYPE_MAP = {
    'organisation': Organisation,
    'employee': User,
    'guest': User
}

@account_bp.route('/')
def login():
    organisations = Organisation.query.all()
    users = User.query.all()
    return render_template('login.html', title='Login', organisations=organisations, users=users)

@account_bp.route('/request_employee_access', methods=['GET', 'POST'])
def request_employee_access():
    if request.method == 'POST':
        email = request.form.get('email')
        organisation = Organisation.query.filter_by(email=email).first()
        if organisation:
            send_email(organisation.email, 'Employee Access Request', f'An employee has requested access to your organisation with email: {email}')
            flash('Request sent to organisation.', 'info')
            return redirect(url_for('account.login'))
        flash('Organisation not found.', 'danger')
    return render_template('login.html')

@account_bp.route('/login/organisation', methods=['GET', 'POST'])
def login_organisation():
    account_type = types_of_accounts[0]
    if request.method == 'POST':
        org_id = request.form.get('organisation')
        password = request.form.get('password')
        organisation = Organisation.query.filter_by(id=org_id).first()

        if organisation and organisation.check_password(password):
            if organisation.verified == 0:
                # Organisation is not verified, redirect to verification
                token = generate_code(organisation.email, account_type)
                resend_verification_email(organisation.email, account_type, token)
                flash('Your account is not verified. A verification email has been sent.', 'warning')
                return redirect(url_for('account.verify_account', email=organisation.email))
            else:
                # Organisation is verified, proceed to login
                login_user(organisation, remember=True)
                flash('Login successful.', 'success')
                return redirect(url_for('main.index'))

        else:
            # Incorrect password
            if organisation:
                send_email(organisation.email)
            flash('Invalid credentials. Please try again.', 'danger')
            return redirect(url_for('account.login'))

    organisations = Organisation.query.all()
    return render_template('login.html', organisations=organisations)

# Employee Login Route
@account_bp.route('/login_employee', methods=['GET', 'POST'])
def login_employee():
    account_type = types_of_accounts[1]
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
    return render_template('index.html', title='Guest Demo', user='Guest')

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
        elif current_user.is_guest:
            return redirect(url_for('main.index', user='Guest'))
    else:
        return redirect(url_for('account.login'))

@account_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@account_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            send_email(user.email, 'Reset Password', 'Click the link below to reset your password.')
            organisation = Organisation.query.get(user.organisation_id)
            send_email(organisation.email, 'Password Reset', f'A password reset link has been sent to {user.email} as they have forgotten their password.')
            flash(f'A password reset link has been sent to your {email} and {organisation.name} has been notified of this change', 'info')
            return redirect(url_for('account.login'))
        flash('Email not found.', 'danger')
        return render_template('forgot_password.html')
    return render_template('forgot_password.html')

@account_bp.route('/register_organisation', methods=['GET', 'POST'])
def register_organisation():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        account_type = types_of_accounts[0]
        organisation_name = form.organisation_name.data
        password = form.password.data
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        email = form.email.data
        new_token = generate_code(email, account_type)
        send_verification_email(email, new_token)
        
        time_of_creation = datetime.now()
        
        new_organisation = Organisation(
            name=organisation_name,
            email=email,
            password=hashed_password,
            logo= 'default.jpg',
            created_at=time_of_creation,
            updated_at=time_of_creation,
            verified=0,
            last_generated_code=new_token,
            last_generated_code_time=time_of_creation
        )
        
        db.session.add(new_organisation)
        db.session.commit()
        send_email(Organisation.email, 'Welcome!', 'Your account has been created.')
        flash('Organisation registered successfully.', 'success')
        return redirect(url_for('account.verify_account'))
    
    return render_template('register.html', form=form)
        

@account_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    db.session.delete(user)
    db.session.commit()
    flash('Account deleted successfully.', 'success')
    return redirect(url_for('account.login'))

@account_bp.route('/verify_account', methods=['GET', 'POST'])
def verify_account():
    if request.method == 'POST':
        verification_code = request.form.get('verification_code')
        email = request.form.get('email')
        account = db.session.query(types_of_accounts[0]).filter_by(email=request.form.get('email')).first()
        account_type = request.form.get('account_type')

        token_verified = verify_code(verification_code, email, account_type)
        
        if token_verified == True:
            account_type.query.filter_by(email=email).first()
            account.verified = 1
            db.session.commit()
            flash('Account successfully verified.', 'success')
            
        else:
            flash('Invalid verification code. Please try again.', 'danger')
            return redirect(url_for('account.verify_account'))

    return render_template('verification.html')

@account_bp.route('/resend_verification', methods=['POST'])
def resend_verification():
    email = request.form['email']
    account_type_str = request.form['account_type']
    token = request.form['token']

    # Get the model class from the account type string
    account_type = ACCOUNT_TYPE_MAP.get(account_type_str)
    if not account_type:
        flash('Invalid account type.', 'danger')
        return redirect(url_for('account.verify_account', email=email, account_type=account_type_str))

    # Verify the token
    token_verified = verify_code(token, email, account_type_str)

    if not token_verified:
        # Token is invalid or expired
        token = None

        # Generate a new verification code
        new_token = generate_code(email, account_type_str)

        # Send the new verification code to the user
        resend_verification_email(email, account_type_str)

        flash('A new verification email has been sent.', 'info')
    else:
        flash('The verification code is still valid.', 'info')
        resend_verification_email(email, account_type_str)
        flash('A new verification email has been sent.', 'info')
    return redirect(url_for('account.verify_account', email=email, account_type=account_type_str))