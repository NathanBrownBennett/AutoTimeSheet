from flask import Flask, request, render_template, send_from_directory, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename
from docx import Document
import json
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'timesheets'
app.config['PROCESSED_FOLDER'] = 'json/daily'
app.config['ALLOWED_EXTENSIONS'] = {'docx', 'pdf'}

# Ensure upload and processed directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_timesheet_data(doc_path):
    doc = Document(doc_path)

    # Initialize dictionary to store extracted data
    timesheet_data = {
        "Employee Name": "",
        "Week Beginning": "",
        "Entries": []
    }

    # Extract the week beginning and employee name from the document
    timesheet_data["Week Beginning"] = doc.paragraphs[-2].text.split("…")[1].strip()
    timesheet_data["Employee Name"] = doc.paragraphs[-1].text.split("…")[1].strip()

    # Extract table data
    table = doc.tables[0]
    for row in table.rows[1:6]:  # Assuming 5 days of data (Mon-Fri)
        cells = row.cells
        entry = {
            "DATE": cells[0].text.strip(),
            "WORK SITE ADDRESS": cells[1].text.strip(),
            "START": cells[2].text.strip(),
            "FINISH": cells[3].text.strip(),
            "LUNCH": cells[4].text.strip(),
            "BASIC HRS": cells[5].text.strip(),
            "O/T 1.5": cells[6].text.strip(),
            "O/T 2.0": cells[7].text.strip()
        }
        timesheet_data["Entries"].append(entry)

    return timesheet_data

def save_timesheet_data(timesheet_data, output_path):
    with open(output_path, 'w') as json_file:
        json.dump(timesheet_data, json_file, indent=4)

def calculate_hours_and_pay(json_path):
    with open(json_path, 'r') as json_file:
        timesheet_data = json.load(json_file)

    # Initialize dictionary for calculated data
    employee_data = {
        "Employee Name": timesheet_data["Employee Name"],
        "Week": timesheet_data["Week Beginning"],
        "Basic": 40.0,
        "X1.5": 0.0,
        "X2.0": 0.0,
        "pay rate/hr": 0,  
        "Annual": 0.00,  
        "per month": 0  
    }

    # Calculate total hours
    for entry in timesheet_data["Entries"]:
        employee_data["Basic"] += float(entry["BASIC HRS"])
        employee_data["X1.5"] += float(entry["O/T 1.5"])
        employee_data["X2.0"] += float(entry["O/T 2.0"])

    calculated_json_path = os.path.join(app.config['PROCESSED_FOLDER'], os.path.basename(json_path).replace('.json', '_calculated.json'))
    with open(calculated_json_path, 'w') as json_file:
        json.dump(employee_data, json_file, indent=4)

    return calculated_json_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        timesheet_data = extract_timesheet_data(file_path)
        timesheet_json_path = os.path.join(app.config['PROCESSED_FOLDER'], filename.replace('.docx', '.json'))
        save_timesheet_data(timesheet_data, timesheet_json_path)

        calculated_json_path = calculate_hours_and_pay(timesheet_json_path)
        return send_from_directory(app.config['PROCESSED_FOLDER'], os.path.basename(calculated_json_path))
    return redirect(request.url)

@app.route('/download_template')
def download_template():
    doc = Document()
    current_date = datetime.now()
    week_start = current_date - timedelta(days=current_date.weekday())
    
    doc.add_heading('Timesheet', 0)
    doc.add_paragraph(f'Week Beginning: {week_start.strftime("%d %B %Y")}')
    
    table = doc.add_table(rows=7, cols=8)
    headers = ["DATE", "WORK SITE ADDRESS", "START", "FINISH", "LUNCH", "BASIC HRS", "O/T 1.5", "O/T 2.0"]
    for i, header in enumerate(headers):
        table.cell(0, i).text = header

    for i in range(1, 6):
        day = week_start + timedelta(days=i-1)
        table.cell(i, 0).text = day.strftime("%a %d")
    
    template_path = os.path.join(app.config['UPLOAD_FOLDER'], 'timesheet_template.docx')
    doc.save(template_path)
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'timesheet_template.docx')

if __name__ == '__main__':
    app.run(debug=True)
