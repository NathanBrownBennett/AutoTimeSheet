from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from ..models import User, Organisation, JobCard, Timesheet
from ..init_extensions import db
from .email_util import send_email
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime


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

    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)
