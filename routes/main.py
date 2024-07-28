from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, current_app
from flask_login import login_user, current_user, login_required
from models import User, Organisation, Timesheet
from util import allowed_file, save_data
import os
from werkzeug.utils import secure_filename
from extensions import db
from routes.email_util import send_email
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def login():
    if request.method == 'POST':
        organisation_id = request.form.get('organisation')
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, organisation_id=organisation_id).first()
        if user and user.check_password(password):
            login_user(user)
            send_email(user.email, 'Login Alert', f'You have logged in from a new device at {datetime.now()}.')
            return redirect(url_for('main.index'))
        flash('Login Unsuccessful. Please check username and password', 'danger')
    organisations = Organisation.query.all()
    return render_template('login.html', organisations=organisations)

@main_bp.route('/login', methods=['GET', 'POST'])
def check_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    else:
        login()

@main_bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html', title='Timesheet Processor')

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
