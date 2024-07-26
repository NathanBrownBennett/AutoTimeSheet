from flask_mail import Message
from flask import current_app as app
from models import Organisation, Config
from extensions import mail 

def send_email(subject, recipients, text_body, html_body=None):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    if html_body:
        msg.html = html_body
    mail.send(msg)

def init_mail(app):
    mail.init_app(app)
    load_email_config(app)
    
def load_email_config(app):
    smtp_config = Config.query.filter_by(name='smtp').first()
    if smtp_config:
        app.config['MAIL_SERVER'] = smtp_config.value
        app.config['MAIL_PORT'] = smtp_config.value
        app.config['MAIL_USE_TLS'] = smtp_config.value
        app.config['MAIL_USERNAME'] = smtp_config.value
        app.config['MAIL_PASSWORD'] = smtp_config.value
        app.config['MAIL_DEFAULT_SENDER'] = smtp_config.value
    else:
        print("SMTP configuration not found in the database.")

def send_update_email(user):
    msg = Message("Account Details Updated", recipients=[user.email])
    msg.body = "Your account details have been updated."
    mail.send(msg)

def request_company_name_change(organisation_id, new_company_name):
    organisation = Organisation.query.get(organisation_id)
    if organisation:
        msg = Message("Request for Company Name Change", recipients=['superadmin@example.com'])
        msg.body = f"Organisation {organisation.name} (ID: {organisation_id}) has requested to change its name to {new_company_name}."
        mail.send(msg)