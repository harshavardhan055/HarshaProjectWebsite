import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash

from extensions import db, login_manager

# ========== Logging Setup ==========
logging.basicConfig(level=logging.DEBUG)

# ========== Flask App Initialization ==========
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ========== App Config ==========
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///harsha_projects.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
app.config["ALLOWED_EXTENSIONS"] = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "svg", "mp4"}
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ========== Initialize Extensions ==========
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# ========== User Loader ==========
from models import User  # ✅ Safe to import now

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ========== DB Init + Admin User ==========
with app.app_context():
    db.create_all()

    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="technicalmaster193@gmail.com",
            password_hash=generate_password_hash("admin"),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        app.logger.info("✅ Admin user created.")

# ========== Import Routes ==========
import routes  # make sure this exists

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

