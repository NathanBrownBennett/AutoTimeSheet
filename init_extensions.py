from app_extensions import db, migrate, login_manager, mail, bcrypt

def init_extensions(app):
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    # New code block
    # Add your code here