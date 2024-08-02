from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from extensions.app_extensions import db, bcrypt

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    server = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    use_tls = db.Column(db.Boolean, default=False)
    use_ssl = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    logo = db.Column(db.String(150))
    organisation_email = db.Column(db.String(100))
    employees = db.relationship('User', backref=db.backref('organisation', lazy=True))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    verified = db.Column(db.Boolean, default=False)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(64), unique=True)
    user = db.relationship('User', backref=db.backref('role', lazy=True))
    
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'), nullable=False)
    organisation = db.relationship('Organisation', backref=db.backref('employees', lazy=True))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    role = db.relationship('Role', backref=db.backref('users', lazy=True))
    organisation = db.relationship('Organisation', backref=db.backref('user_organisations', lazy=True))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    last_login_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    number_of_logins = db.Column(db.Integer, default=0)
    verified = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

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
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Timesheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    date_commencing = db.Column(db.Date, nullable=False)
    hours_worked = db.Column(db.Float, nullable=False)
    user = db.relationship('User', backref=db.backref('timesheets', lazy=True))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='to-do')  # to-do, in-progress, completed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Task {self.title}>'
    
class SuperAdmin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    Role = db.relationship('Role', backref=db.backref('super_admin', lazy=True))
    Organisation = db.relationship('Organisation', backref=db.backref('super_admin', lazy=True))

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<SuperAdmin {self.username}>'
