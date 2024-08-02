from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Database created successfully.")