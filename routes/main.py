from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, current_app
from flask_login import login_user, current_user, login_required, logout_user
from models import User, Organisation, Timesheet, JobCard
from Server_Side_Processing.util import allowed_file, save_data
import os
from werkzeug.utils import secure_filename
from extensions.app_extensions import db, login_manager, mail, bcrypt
from routes.email_util import send_email

main_bp = Blueprint('main', __name__)

@main_bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html', title='Buisiness Productivity App')

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
