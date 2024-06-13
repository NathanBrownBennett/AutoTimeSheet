from flask import Flask, request, render_template, send_from_directory, redirect, url_for, jsonify
import os
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

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'
app.config['UPLOAD_FOLDER'] = 'timesheets'
app.config['PROCESSED_FOLDER'] = 'json/daily'
app.config['ALLOWED_EXTENSIONS'] = {'docx', 'pdf'}

# Ensure upload and processed directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_timesheet_data(timesheet_data, output_path):
    with open(output_path, 'w') as json_file:
        json.dump(timesheet_data, json_file, indent=4)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Timesheet Processor')

@app.route('/info.html')
def info():
    return render_template('info.html', title='Application Information')

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

        calculated_json_path = extract_daily_timesheet_data(timesheet_json_path)
        return send_from_directory(app.config['PROCESSED_FOLDER'], os.path.basename(calculated_json_path))
    return redirect(request.url)

@app.route('/download_template')

def set_row_height(row, height):
    """
    Set the height of a row in the table.
    """
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(qn('w:val'), str(height))
    trHeight.set(qn('w:hRule'), "atLeast")
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
    app.run(debug=True)
