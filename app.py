# app.py
from flask import Flask
from extensions.init_extensions import setup, login_manager, db, bcrypt, mail, migrate
from models import User

def create_app():
    print("setting app environment var")
    app = Flask(__name__)
    print("App environment var set")
    app.config.from_object('routes.sqlalch_config.Config')
    print("App configured")
    
    login_manager.login_view = 'account.login'
    login_manager.login_message_category = 'info'
    print("Login manager configured")
    
    setup(app)
    print("Extensions initialized")
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.main import main_bp
    print("Imported main_bp spinning up main_bp")
    app.register_blueprint(main_bp)
    
    from routes.account import account_bp
    print("Imported account_bp spinning up account_bp")
    app.register_blueprint(account_bp)
    
    from routes.tasks import tasks_bp
    print("Imported tasks_bp spinning up tasks_bp")
    app.register_blueprint(tasks_bp)
    
    from routes.admin import admin_bp
    print("Imported admin spinning up admin_bp")
    app.register_blueprint(admin_bp)
    
    return app

if __name__ == "__main__":
    print("Running app.py")
    app = create_app()
    print("App created")
    app.run(debug=True, host='0.0.0.0')
    print("App closed")
