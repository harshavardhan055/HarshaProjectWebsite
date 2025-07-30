import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from models import User  # Make sure models.py exists and includes User model

# ========== Logging Setup ==========
logging.basicConfig(level=logging.DEBUG)

# ========== SQLAlchemy Base ==========
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# ========== Flask App Initialization ==========
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Apply ProxyFix for Render or similar services
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ========== App Config ==========
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///harsha_projects.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload limit

# File upload settings
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
app.config["ALLOWED_EXTENSIONS"] = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "svg", "mp4"}
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ========== Initialize Extensions ==========
db.init_app(app)

# ========== Flask-Login Setup ==========
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# ========== Create Database and Admin ==========
with app.app_context():
    db.create_all()

    # Create admin user if not exists
    if not User.query.filter_by(username="admin").first():
        admin_user = User(
            username="admin",
            email="technicalmaster193@gmail.com",
            password_hash=generate_password_hash("admin"),  # 🔐 Consider using a secure password
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        app.logger.info("✅ Admin user created.")

# ========== User Loader for Flask-Login ==========
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ========== Import Routes ==========
import routes  # Ensure routes.py exists with Flask views defined
