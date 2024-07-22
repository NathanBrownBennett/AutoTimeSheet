from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref=db.backref('users', lazy=True))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        return self.role.name == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'

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
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Timesheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    mon_hours = db.Column(db.Float, default=0.0)
    tue_hours = db.Column(db.Float, default=0.0)
    wed_hours = db.Column(db.Float, default=0.0)
    thu_hours = db.Column(db.Float, default=0.0)
    fri_hours = db.Column(db.Float, default=0.0)
    sat_hours = db.Column(db.Float, default=0.0)
    sun_hours = db.Column(db.Float, default=0.0)
    total_hours = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def calculate_total_hours(self):
        self.total_hours = self.mon_hours + self.tue_hours + self.wed_hours + self.thu_hours + self.fri_hours
