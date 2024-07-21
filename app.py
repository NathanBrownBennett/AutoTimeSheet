from flask import Flask, request, render_template, send_from_directory, redirect, url_for, jsonify, flash
import os
from app import SMTPConfig
from werkzeug.utils import secure_filename
from docx import Document
import json
from datetime import datetime, timedelta
from docx.enum.section import WD_ORIENTATION
from docx.shared import Inches
from timesheet2json import extract_timesheet_data
from totalHourDict import extract_daily_timesheet_data
from updateExcel import update_excel
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import nsdecls, qn as xml_qn
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import json
import requests
import msal
import openpyxl
import sqlite3

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'
app.config['UPLOAD_FOLDER'] = 'timesheets'
app.config['PROCESSED_FOLDER'] = 'json/daily'
app.config['ALLOWED_EXTENSIONS'] = {'docx', 'pdf'}

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'docx', 'pdf'}

def load_email_config():
    smtp_config = SMTPConfig.query.first()
    if smtp_config:
        app.config['MAIL_SERVER'] = smtp_config.mail_server
        app.config['MAIL_PORT'] = smtp_config.mail_port
        app.config['MAIL_USE_TLS'] = smtp_config.use_tls
        app.config['MAIL_USERNAME'] = smtp_config.username
        app.config['MAIL_PASSWORD'] = smtp_config.password
        app.config['MAIL_DEFAULT_SENDER'] = smtp_config.default_sender
    else:
        print("SMTP configuration not found in the database.")


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

# Ensure upload and processed directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def get_config():
    """Retrieve configuration data from the config table in msal.db"""
    conn = sqlite3.connect('msal.db')
    cur = conn.cursor()
    cur.execute("SELECT name, value FROM config")

    config_data = {name: value for name, value in cur.fetchall()}
    return config_data

config = get_config()
client_id = config.get('client_id')
client_secret = config.get('client_secret')
tenant_id = config.get('tenant_id')
scope = config.get('scope')
graph_api_endpoint = config.get('graph_api_endpoint')
excel_file_path = config.get('excel_file_path')

#MODELS

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'employee'

class Timesheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), nullable=False)
    filepath = db.Column(db.String(150), nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_timesheet_data(timesheet_data, output_path):
    with open(output_path, 'w') as json_file:
        json.dump(timesheet_data, json_file, indent=4)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Timesheet Processor')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        timesheets = Timesheet.query.all()
    else:
        timesheets = Timesheet.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', timesheets=timesheets)

@app.route('/info.html')
def info():
    return render_template('info.html', title='Application Information')

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        new_timesheet = Timesheet(filename=filename, filepath=filepath, user_id=current_user.id)
        db.session.add(new_timesheet)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return redirect(request.url)

@app.route('/approve/<int:timesheet_id>')
@login_required
def approve_timesheet(timesheet_id):
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    timesheet = Timesheet.query.get_or_404(timesheet_id)
    timesheet.approved = True
    db.session.commit()
    update_excel_file(timesheet.filepath)
    send_approval_email(timesheet.user_id)
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:timesheet_id>')
@login_required
def delete_timesheet(timesheet_id):
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    timesheet = Timesheet.query.get_or_404(timesheet_id)
    db.session.delete(timesheet)
    db.session.commit()
    return redirect(url_for('dashboard'))

def get_access_token(client_id, client_secret, tenant_id, scope):
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret,
    )
    
    result = app.acquire_token_for_client(scopes=scope)
    
    if "access_token" in result:
        return result["access_token"]
    else:
        print("Failed to obtain access token")
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))  # You might want to log this for later correlation investigation.
        return None


def update_excel_file(filepath):
    # Load calculated employee data
    calculated_json_path = '/mnt/data/employee_data.json'
    with open(calculated_json_path, 'r') as json_file:
        employee_data = json.load(json_file)
    
    # Get access token
    access_token = get_access_token(client_id, client_secret, tenant_id, scope)
    
    # Update the Excel file
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    workbook_url = f"{graph_api_endpoint}/me/drive/root:/{excel_file_path}:/workbook/worksheets"
    response = requests.get(workbook_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to get worksheet. Status code: {response.status_code}")
        return

    worksheets = response.json()["value"]
    sheet_id = worksheets[0]["id"]  # Assuming we're updating the first worksheet

    cell_updates = [
        {
            "range": "A1",
            "values": [[
                "Employee Name", "Week", "Basic", "X1.5", "X2.0", "pay rate/hr", "Annual", "per month"
            ]]
        },
        {
            "range": "A2",
            "values": [[
                employee_data["Employee Name"],
                employee_data["Week"],
                employee_data["Basic"],
                employee_data["X1.5"],
                employee_data["X2.0"],
                employee_data["pay rate/hr"],
                employee_data["Annual"],
                employee_data["per month"]
            ]]
        }
    ]

    for update in cell_updates:
        update_url = f"{graph_api_endpoint}/me/drive/root:/{excel_file_path}:/workbook/worksheets/{sheet_id}/range(address='{update['range']}')"
        response = requests.patch(update_url, headers=headers, json={"values": update["values"]})
        if response.status_code != 200:
            print(f"Failed to update cell {update['range']}. Status code: {response.status_code}")
            return

    print("Excel sheet updated successfully.")
    
def send_approval_email(user_id):
    user = User.query.get(user_id)
    msg = Message("Timesheet Approved", recipients=[user.email])
    msg.body = "Your timesheet has been approved and updated."
    mail.send(msg)


@app.route('/download_template')
def set_row_height(row, height):
    """
    Set the height of a row in the table.
    """
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(xml_qn('w:val'), str(height))
    trHeight.set(xml_qn('w:hRule'), "atLeast")
    trPr.append(trHeight)
    
def download_template():
    doc = Document()
    current_date = datetime.now()
    week_start = current_date - timedelta(days=current_date.weekday())

    section = doc.sections[0]
    section.orientation = WD_ORIENTATION.LANDSCAPE
    section.page_width = Inches(11)
    section.page_height = Inches(8.5)

    doc.add_heading('GMT ELECTRICAL SERVICES LTD – WEEKLY TIMESHEET', 0)
    doc.add_paragraph(f'Week Beginning: {week_start.strftime("%d %B %Y")}')
    doc.add_paragraph(f'Name:' f'{'_'*20}')

    table = doc.add_table(rows=7, cols=8, style='Table Grid')
    headers = ["DATE", "WORK SITE ADDRESS", "START", "FINISH", "LUNCH", "BASIC HRS", "O/T 1.5", "O/T 2.0"]

    # Calculate column width
    total_width = Inches(11)  # Page width
    column_width = total_width / len(headers)
    
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.width = column_width
        cell.text = header

    for i in range(1, 7):
        row = table.rows[i]
        set_row_height(row, Pt(46))  # Set row height to accommodate roughly four lines of text
        if i < 6:
            day = week_start + timedelta(days=i-1)
            row.cells[0].text = day.strftime("%a %d")

    # Ensure table spans full width
    for row in table.rows:
        for cell in row.cells:
            cell.width = column_width

    template_path = os.path.join(app.config['UPLOAD_FOLDER'], 'timesheet_template.docx')
    doc.save(template_path)
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'timesheet_template.docx')

if __name__ == '__main__':
    load_email_config()
    app.run(debug=True)
