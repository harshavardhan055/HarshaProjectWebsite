from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile("config.py", silent=False) # Changed silent to False for initial setup

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main_routes.login' # Specify the login view

from models import * # Make sure models are imported so db.create_all works
from routes import main_routes # Import and register blueprint here
app.register_blueprint(main_routes)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
