from flask import Flask
from extensions import db, migrate, login_manager, bcrypt
from models import User
from routes.admin import admin_bp
from routes.account import account_bp
from routes.main import main_bp
from routes.tasks import tasks_bp
from routes.email_util import load_email_config

def create_app():
    app = Flask(__name__)
    app.config.from_object('routes.sqlalch_config.Config')  # Updated to sqlalch_config

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Register Blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tasks_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        load_email_config(app)  # Pass the app instance

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
