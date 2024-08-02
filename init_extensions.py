from app_extensions import db, migrate, login_manager, mail, bcrypt

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