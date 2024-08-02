from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions.app_extensions import db
from models import User, Role, JobCard, Timesheet
import jsonify
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role_name = request.form.get('role')
        role = Role.query.filter_by(name=role_name).first()
        if role is None:
            role = Role(name=role_name)
            db.session.add(role)
            db.session.commit()
        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully.', 'success')

    users = User.query.all()
    return render_template('admin.html', users=users)

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

        # Save picture and video
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
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('create_job_card.html')

@admin_bp.route('/export_job_cards', methods=['GET'])
@login_required
def export_job_cards():
    job_cards = JobCard.query.all()
    data = []
    for job in job_cards:
        data.append({
            'job_id': job.job_id,
            'description': job.description,
            'location': job.location,
            'company': job.company,
            'date': job.date.strftime('%Y-%m-%d'),
            'price': job.price,
            'completed_by': job.completed_by,
            'duration': job.duration
        })
    # Export data to a CSV or any suitable format
    return jsonify(data)

@admin_bp.route('/create_timesheet', methods=['GET', 'POST'])
@login_required
def create_timesheet():
    if request.method == 'POST':
        week_start = request.form.get('week_start')
        mon_hours = request.form.get('mon_hours', 0.0)
        tue_hours = request.form.get('tue_hours', 0.0)
        wed_hours = request.form.get('wed_hours', 0.0)
        thu_hours = request.form.get('thu_hours', 0.0)
        fri_hours = request.form.get('fri_hours', 0.0)
        sat_hours = request.form.get('sat_hours', 0.0)
        sun_hours = request.form.get('sun_hours', 0.0)
        timesheet = Timesheet(
            user_id=current_user.id,
            week_start=week_start,
            mon_hours=mon_hours,
            tue_hours=tue_hours,
            wed_hours=wed_hours,
            thu_hours=thu_hours,
            fri_hours=fri_hours,
            sat_hours=sat_hours,
            sun_hours=sun_hours
        )
        timesheet.calculate_total_hours()
        db.session.add(timesheet)
        db.session.commit()
        flash('Timesheet created successfully.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('create_timesheet.html')

@admin_bp.route('/export_timesheets', methods=['GET'])
@login_required
def export_timesheets():
    timesheets = Timesheet.query.filter_by(user_id=current_user.id).all()
    data = []
    for sheet in timesheets:
        data.append({
            'week_start': sheet.week_start.strftime('%Y-%m-%d'),
            'mon_hours': sheet.mon_hours,
            'tue_hours': sheet.tue_hours,
            'wed_hours': sheet.wed_hours,
            'thu_hours': sheet.thu_hours,
            'fri_hours': sheet.fri_hours,
            'sat_hours': sheet.sat_hours,
            'sun_hours': sheet.sun_hours,
            'total_hours': sheet.total_hours
        })
    # Export data to a CSV or any suitable format
    return jsonify(data)
