from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from ..models import User, Organisation, JobCard, Timesheet
from ..init_extensions import db, login_manager, mail, bcrypt
from .email_util import send_email, send_verification_email
from werkzeug.security import generate_password_hash
from ..Server_Side_Processing.verify_paseto import generate_code
from werkzeug.utils import secure_filename
import os
from datetime import datetime

types_of_accounts = [Organisation, User, 'employee', 'guest', 'admin']

ACCOUNT_TYPE_MAP = {
    'organisation': Organisation,
    'employee': User,
    'guest': User
}

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role_name = request.form.get('role')
        organisation = current_user.organisation

        if not organisation:
            flash('No organisation found.', 'danger')
            return redirect(url_for('admin.admin_dashboard'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin.admin_dashboard'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password_hash=hashed_password, role_name=role_name, organisation=organisation)
        db.session.add(new_user)
        db.session.commit()

        send_email(new_user.email, 'Account Created', f'Your account has been created with username: {username}')
        send_email(organisation.email, 'New User Created', f'A new user has been created with username: {username}')

        flash('User created successfully.', 'success')
        
@admin_bp.route('/register_employee', methods=['GET', 'POST'])
@login_required
def register_employee():
    if current_user.is_admin:
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            role_name = request.form.get('role')
            organisation = current_user.organisation
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            existing_user = User.query.filter_by(username=username).first()
            account_type = types_of_accounts[2]
            if username == existing_user:
                flash('Username already exists.', 'danger')
                return redirect(url_for('admin.register_employee'))
            time_of_creation = datetime.now()
            new_token = generate_code(email, account_type)
            send_verification_email(email, new_token)
            new_user = User(
                username=username,
                password=hashed_password,
                email=email,
                organisation_id=current_user.id,
                profile_picture= 'default.jpg',
                created_at=time_of_creation,
                updated_at=time_of_creation,
                verified=0,
                last_generated_code=new_token,
                last_generated_code_time=time_of_creation
                )
            db.session.add(new_user)
            db.session.commit()
            flash('Employee registered successfully.', 'success')
            return redirect(url_for('account.register_employee'))
    return render_template('register_employee.html')

    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)
