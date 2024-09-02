# routes/email_util.py
from flask import url_for, current_app
from flask_mail import Mail, Message
from ..init_extensions import db
from ..models import Organisation, User
from .sqlalch_config import Config, Mail_Configs
from ..Server_Side_Processing.verify_paseto import generate_code
from ..init_extensions import mail
from dotenv import load_dotenv
import os
import smtplib
from flask import current_app
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import requests
from requests.auth import HTTPBasicAuth

mail = Mail()
load_dotenv()

def init_mail(app):
    mail.init_app(app)
    load_email_config(app)
    
def get_oauth2_token():
    tenant_id = os.getenv('TENANT_ID')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    authority_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://outlook.office365.com/.default'
    }

    response = requests.post(authority_url, headers=headers, data=data, auth=HTTPBasicAuth(client_id, client_secret))
    response.raise_for_status()
    token = response.json()['access_token']
    
    return token

def send_email(subject, recipient, body):
    access_token = get_oauth2_token()
    smtp_server = "smtp.office365.com"
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = os.getenv('EMAIL')
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("USERNAME", access_token)
        server.sendmail(os.getenv('EMAIL'), recipient, msg.as_string())
        server.quit()

def load_email_config(app):
    with app.app_context():  # Ensure this is within the application context
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
        app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
        app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
        app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
        mail.init_app(app)

def send_update_email(user):
    try:
        msg = Message("Account Details Updated", recipients=[user.email])
        msg.body = "Your account details have been updated."
        mail.send(msg)
    except ConnectionRefusedError as e:
        current_app.logger.error(f"Error: {e}")

def request_company_name_change(organisation_id, new_company_name):
    organisation = Organisation.query.get(organisation_id)
    try:
        if organisation:
            msg = Message("Request for Company Name Change", recipients=['nathanbrown-bennett@hotmail.com'])
            msg.body = f"Organisation {organisation.name} (ID: {organisation_id}) has requested to change its name to {new_company_name}."
            mail.send(msg)
        else:
            raise Exception("Organisation not found.")
    except Exception as e:
        current_app.logger.error(f"Error: {e}")

def send_verification_email(email, account_type):
    try:
        token = generate_code(email, account_type)
        verification_url = url_for('account.verify_account', token=token, _external=True)
        msg = Message("Verification Email", recipients=[email])
        msg.body = f'Please verify your account by clicking the following link: {verification_url}'
        mail.send(msg)
    except ConnectionRefusedError as e:
        current_app.logger.error(f"Error: {e}")

def send_confirmation_email(email):
    try:
        subject = "Account Verified"
        message = "Your account has been successfully verified."
        send_email(subject, [email], message)
    except ConnectionRefusedError as e:
        current_app.logger.error(f"Error: {e}")

def resend_verification_email(email, account_type, token):
    try:
        token = generate_code(email, account_type)
        verification_url = url_for('account.verify_account', token=token, _external=True)
        msg = Message("Verification Email", recipients=[email])
        msg.body = f'Please verify your account by clicking the following link: {verification_url}'
        mail.send(msg)
        send_verification_email(email, account_type, token)
    except ConnectionRefusedError as e:
        current_app.logger.error(f"Error: {e}")