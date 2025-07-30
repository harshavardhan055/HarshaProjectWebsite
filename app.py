import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

# ========== Logging Setup ==========
logging.basicConfig(level=logging.DEBUG)

# ========== SQLAlchemy Base Class ==========
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# ========== Flask App Configuration ==========
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Proxy fix for deployment platforms like Render
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ========== Database Configuration ==========
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///harsha_projects.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload limit

# ========== File Upload Configuration ==========
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
app.config["ALLOWED_EXTENSIONS"] = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "svg", "mp4"}

# Create the upload directory if it doesn't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ========== Initialize SQLAlchemy ==========
db.init_app(app)

# ========== Flask-Login Setup ==========
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# ========== Load User Model & Create Admin ==========
with app.app_context():
    from models import User  # Make sure models.py defines User

    # Create tables
    db.create_all()

    # Create admin user if not already exists
    if not User.query.filter_by(username="admin").first():
        admin_user = User(
            username="admin",
            email="technicalmaster193@gmail.com",  # ✅ Replace with your Gmail
            password_hash=generate_password_hash("admin"),  # ⚠️ Replace with strong password in production
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        app.logger.info("✅ Admin user created.")

# ========== Flask-Login User Loader ==========
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# ========== Import Routes ==========
# Assuming you have a file named routes.py or a routes folder with __init__.py
try:
    import routes
except ImportError:
    app.logger.warning("⚠️ No routes.py found. Add your routes or blueprint.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
