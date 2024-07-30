# app.py
from flask import Flask
from init_extensions import init_extensions
from models import User, Organisation, JobCard, Timesheet
from app_extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object('routes.sqlalch_config.Config')
    
    init_extensions(app)
    db.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @login_manager.request_loader
    def load_organisation(organisation_id):
        return Organisation.query.get(int(organisation_id))
    
    @login_manager.request_loader
    def load_job_card(job_card_id):
        return JobCard.query.get(int(job_card_id))
    
    @login_manager.request_loader
    def load_timesheet(timesheet_id):
        return Timesheet.query.get(int(timesheet_id))

    from routes.main import main_bp
    app.register_blueprint(main_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
