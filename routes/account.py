from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from models import User, Organisation
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from routes.email_util import send_email

account_bp = Blueprint('account', __name__)

@account_bp.route('/account_settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        # Handle the form submission to update account settings
        pass
    return render_template('account_settings.html')

@account_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@account_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
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
        return redirect(url_for('account.login'))
    return render_template('register.html')
