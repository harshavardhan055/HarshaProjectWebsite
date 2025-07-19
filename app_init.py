from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os # Import os module

# Get the absolute path to the directory where app_init.py resides
# This ensures that config.py is loaded relative to app_init.py
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__) # Remove instance_relative_config=True
# Load config.py from the same directory as app_init.py
app.config.from_pyfile(os.path.join(basedir, 'config.py'), silent=False)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main_routes.login' # Assuming 'main_routes' is your blueprint name

from models import User # Import User model for Flask-Login

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import and register blueprints AFTER app and db are initialized
from routes import main_routes
app.register_blueprint(main_routes)

# Import Jinja filters (they also depend on 'app')
import jinja_filters
