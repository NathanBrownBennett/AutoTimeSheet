from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'smtp_settings.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class SMTPSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail_server = db.Column(db.String(120), nullable=False)
    mail_port = db.Column(db.Integer, nullable=False)
    mail_use_tls = db.Column(db.Boolean, default=True)
    mail_username = db.Column(db.String(120), nullable=False)
    mail_password = db.Column(db.String(120), nullable=False)
    mail_default_sender = db.Column(db.String(120), nullable=False)

def get_smtp_settings_from_user():
    print("Please enter your SMTP settings:")
    mail_server = input("Mail Server: ")
    mail_port = int(input("Mail Port: "))
    mail_use_tls = input("Use TLS (True/False): ").lower() in ('true', 't', '1', 'yes', 'y')
    mail_username = input("Mail Username: ")
    mail_password = input("Mail Password: ")
    mail_default_sender = input("Mail Default Sender: ")
    
    return SMTPSettings(
        mail_server=mail_server,
        mail_port=mail_port,
        mail_use_tls=mail_use_tls,
        mail_username=mail_username,
        mail_password=mail_password,
        mail_default_sender=mail_default_sender
    )

if __name__ == '__main__':
    db.create_all()
    smtp_settings = get_smtp_settings_from_user()
    db.session.add(smtp_settings)
    db.session.commit()
    print("SMTP settings saved successfully.")