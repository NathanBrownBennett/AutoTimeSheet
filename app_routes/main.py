from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, current_app
from flask_login import login_user, current_user, login_required, logout_user
from ..models import User, Organisation, Timesheet, JobCard
from ..Server_Side_Processing.util import allowed_file, save_data
import os
from werkzeug.utils import secure_filename
from ..init_extensions import db, login_manager, mail, bcrypt
from .email_util import send_email
from .tasks import create_task, delete_task, update_task, move_task

main_bp = Blueprint('main', __name__)

@main_bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html', title='Buisiness Productivity App', user=current_user)

@main_bp.route('/info', methods=['GET', 'POST'])
def info():
    return render_template('info.html', title='Info')

@main_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        new_timesheet = Timesheet(filename=filename, filepath=filepath, user_id=current_user.id)
        db.session.add(new_timesheet)
        db.session.commit()
        send_email(current_user.email, 'Timesheet Uploaded', 'A new timesheet has been uploaded.')
        return redirect(url_for('main.index'))
    return redirect(request.url)

@main_bp.route('/#', methods=['GET'])
def createTask():
    create_task()
    delete_task()
    update_task()
    move_task()

@main_bp.route('/create_timesheet', methods=['GET', 'POST'])
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

@main_bp.route('/create_job_card', methods=['GET', 'POST'])
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

