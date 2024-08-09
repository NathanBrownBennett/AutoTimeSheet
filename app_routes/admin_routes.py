from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from init_extensions import db
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
