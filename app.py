# app.py
from flask import Flask
from .init_extensions import setup, login_manager, db
#import init_extensions
from .models import User
from .app_routes import account, tasks, admin, main
from .app_routes.sqlalch_config import Config
from dotenv import load_dotenv

def create_app(config_class=Config):
    print("setting app environment var")
    app = Flask(__name__)
    print("App environment var set")
    app.config.from_object(Config)
    print("App configured")
    
    #login_manager = init_extensions.login_manager
    #setup = init_extensions.setup
    load_dotenv()
    
    login_manager.login_view = 'account.login'
    login_manager.login_message_category = 'info'
    print("Login manager configured")
    
    setup(app)
    print("Extensions initialized")
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .app_routes.main import main_bp
    print("Imported main_bp spinning up main_bp")
    app.register_blueprint(main_bp)
    
    from .app_routes.account import account_bp
    print("Imported account_bp spinning up account_bp")
    app.register_blueprint(account_bp, url_prefix='/')
    
    from .app_routes.tasks import tasks_bp
    print("Imported tasks_bp spinning up tasks_bp")
    app.register_blueprint(tasks_bp)
    
    from .app_routes.admin import admin_bp
    print("Imported admin spinning up admin_bp")
    app.register_blueprint(admin_bp)
    
    return app

if __name__ == "__main__":
    print("Running app.py")
    app = create_app()
    print("App created")
    app.run(debug=True, port='5000', host='0.0.0.0')
    print("App closed")
