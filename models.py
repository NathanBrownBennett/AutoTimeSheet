from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from .init_extensions import db, bcrypt
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#import os

##Base = declarative_base()
#basedir = os.path.abspath(os.path.dirname(__file__))

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
    email = db.Column(db.String(100))
    password = db.Column(db.String(60), nullable=False)
    employees = db.relationship('User', backref='organisation', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    verified = db.Column(db.Boolean, default=False)
    last_generated_code = db.Column(db.String(6))
    last_generated_code_time = db.Column(db.DateTime)
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy=True)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), db.ForeignKey('user.email'), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    last_login_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    number_of_logins = db.Column(db.Integer, default=0)
    verified = db.Column(db.Boolean, default=False)
    last_generated_code = db.Column(db.String(6))
    last_generated_code_time = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role.role == 'admin'

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
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    role = db.relationship('Role', backref=db.backref('super_admins', lazy=True))
    organisation = db.relationship('Organisation', backref=db.backref('super_admins', lazy=True))

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<SuperAdmin {self.username}>'
    
#SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, '..', 'databases', 'instance', 'site.db')
#engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
#Base.metadata.create_all(bind=engine)
#
#Session = sessionmaker(bind=engine)
#session = Session()
#
#p1 = Config(name='config1', server='server1', port=8080, use_tls=True, use_ssl=False, username='user1', password='password1')
#p2 = Organisation(name='org1', logo='logo1', organisation_email='org1@example.com', verified=True)
#p3 = Role(role='role1')
#p4 = Employee(name='employee1', email='employee1@example.com', phone='1234567890', address='address1', organisation_id=1, role_id=1)
#p5 = User(username='user1', role_id=1, organisation_id=1)
#p6 = JobCard(job_id='job1', description='description1', location='location1', company='company1', date=datetime.now().date(), price=100.0, completed_by='user1', duration=2.5)
#p7 = Timesheet(user_id=1, week_start=datetime.now().date(), date_commencing=datetime.now().date(), hours_worked=8.0)
#p8 = SuperAdmin(username='admin1', role_id=1, organisation_id=1)
#p9 = Task(title='task1', description='task description1', status='to-do', user_id=1)
#
#session.add_all([p1, p2, p3, p4, p5, p6, p7, p8, p9])
#session.commit()"""