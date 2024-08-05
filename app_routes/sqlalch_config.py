import os

basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'databases', 'instance', 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    db_name = 'site.db'
    
class Folder_Configs:
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'docx', 'pdf'}
    STATIC_FOLDER = 'static'
    PROCESSED_FOLDER = 'json/daily'

class Mail_Configs:
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.example.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
