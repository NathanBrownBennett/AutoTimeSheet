from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

db = SQLAlchemy()

class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    logo = db.Column(db.String(150))

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    role = db.relationship('Role', backref=db.backref('users', lazy=True))
    organisation = db.relationship('Organisation', backref=db.backref('employees', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role.name == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'

class Timesheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), nullable=False)
    filepath = db.Column(db.String(150), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    date_commencing = db.Column(db.Date, nullable=False)
    hours_worked = db.Column(db.Float, nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    user = db.relationship('User', backref=db.backref('timesheets', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    approved = db.Column(db.Boolean, default=False)

class JobCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    completed_by = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String(100))
    video = db.Column(db.String(100))
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    status = db.Column(db.String(50), nullable=False, default='to-do')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

