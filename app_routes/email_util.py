# routes/email_util.py
from flask import url_for, current_app
from flask_mail import Mail, Message
from ..init_extensions import db
from ..models import Organisation
from .sqlalch_config import Config, Mail_Configs
from ..Server_Side_Processing.verify_paseto import generate_paseto_token
from ..init_extensions import mail
mail = Mail()

def init_mail(app):
    mail.init_app(app)
    load_email_config(app)

def send_email(subject, recipients, body):
    msg = Message(subject, recipients=recipients)
    msg.body = body
    mail.send(msg)

def load_email_config(app):
    with app.app_context():  # Ensure this is within the application context
        smtp_config = Config.query.filter_by(name='smtp').first()
        if smtp_config:
            app.config['MAIL_SERVER'] = smtp_config.server
            app.config['MAIL_PORT'] = smtp_config.port
            app.config['MAIL_USE_TLS'] = smtp_config.use_tls
            app.config['MAIL_USE_SSL'] = smtp_config.use_ssl
            app.config['MAIL_USERNAME'] = smtp_config.username
            app.config['MAIL_PASSWORD'] = smtp_config.password
        mail.init_app(app)

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

def send_verification_email(user):
    token = generate_paseto_token(user.email, user.account_type)
    verification_url = url_for('account.verify', token=token, _external=True)
    msg = Message("Verification Email", recipients=[user.email])
    msg.body = f'Please verify your account by clicking the following link: {verification_url}'
    mail.send(msg)

def send_confirmation_email(email):
    subject = "Account Verified"
    message = "Your account has been successfully verified."
    send_email(subject, [email], message)

def resend_verification_email(email, account_type):
    token = generate_paseto_token(email, account_type)
    send_verification_email(email, account_type, token)