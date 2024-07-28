# app.py
from flask import Flask
from extensions import db, login_manager, mail
from routes.sqlalch_config import Config
from models import User, Organisation, JobCard, Timesheet

def create_app(config_class=Config):
    app.config.from_object(config_class)
    with app.app_context():
        db.init_app(app)
        login_manager.init_app(app)
        mail.init_app(app)
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        from routes.main import main_bp
        from routes.admin import admin_bp
        from routes.account import account_bp 
        from routes.tasks import tasks_bp

        app.register_blueprint(main_bp)  
        app.register_blueprint(admin_bp) 
        app.register_blueprint(account_bp)
        app.register_blueprint(tasks_bp)

        #from routes.email_util import load_email_config
        #load_email_config(app)

        return app

if __name__ == "__main__":
    app = Flask(__name__)
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
