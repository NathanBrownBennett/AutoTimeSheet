from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
bcrypt = Bcrypt()

def setup(app):
	print("Setting up extensions")
	bcrypt.init_app(app)
	print("bcrypt initialized")
	db.init_app(app)
	print("db initialized")
	migrate.init_app(app, db)
	print("migrate initialized")
	login_manager.init_app(app)
	print("login_manager initialized")
	mail.init_app(app)
	print("mail initialized")