from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import User, Organisation, JobCard, Timesheet
from init_extensions import db
from routes.email_util import send_email
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

@admin_bp.route('/create_job_card', methods=['GET', 'POST'])
@login_required
def create_job_card():
    if request.method == 'POST':
        job_id = request.form.get('job_id')
        description = request.form.get('description')
        location = request.form.get('location')
        company = request.form.get('company')
        date = request.form.get('date')
        price = request.form.get('price')
        completed_by = request.form.get('completed_by')
        duration = request.form.get('duration')
        picture = request.files.get('picture')
        video = request.files.get('video')

        picture_filename = secure_filename(picture.filename)
        video_filename = secure_filename(video.filename)
        picture.save(os.path.join('static/uploads', picture_filename))
        video.save(os.path.join('static/uploads', video_filename))

        job_card = JobCard(
            job_id=job_id,
            description=description,
            location=location,
            company=company,
            date=date,
            price=price,
            completed_by=completed_by,
            duration=duration,
            picture=picture_filename,
            video=video_filename
        )
        db.session.add(job_card)
        db.session.commit()
        flash('Job card created successfully.', 'success')
        send_email(current_user.email, 'Job Card Created', 'A new job card has been created.')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('create_job_card.html')

@admin_bp.route('/create_timesheet', methods=['GET', 'POST'])
@login_required
def create_timesheet():
    if request.method == 'POST':
        week_start = request.form.get('week_start')
        date_commencing = request.form.get('date_commencing')
        hours_worked = request.form.get('hours_worked')
        timesheet = Timesheet(
            user_id=current_user.id,
            week_start=week_start,
            date_commencing=date_commencing,
            hours_worked=hours_worked
        )
        db.session.add(timesheet)
        db.session.commit()
        flash('Timesheet created successfully.', 'success')
        send_email(current_user.email, 'Timesheet Created', 'A new timesheet has been created.')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('create_timesheet.html')
