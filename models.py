from app_init import db # Import db from app_init
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    about = db.Column(db.Text)
    profile_photo = db.Column(db.String(300))

    projects = db.relationship("Project", backref="owner", lazy=True)
    testings = db.relationship("Testing", backref="owner", lazy=True)
    # project_views = db.relationship("ProjectView", backref="user", lazy=True) # Uncomment if ProjectView is used

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False) # Added slug for unique URLs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Paths to uploaded files
    image_path = db.Column(db.String(255))
    video_path = db.Column(db.String(255))
    circuit_diagram_path = db.Column(db.String(255))

    # Text content stored directly in DB
    description = db.Column(db.Text)
    code = db.Column(db.Text)
    connections = db.Column(db.Text)
    procedure = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Testing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False) # Added slug for unique URLs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Paths to uploaded files
    image_path = db.Column(db.String(255))
    video_path = db.Column(db.String(255))
    circuit_diagram_path = db.Column(db.String(255))

    # Text content stored directly in DB
    description = db.Column(db.Text)
    code = db.Column(db.Text)
    connections = db.Column(db.Text)
    procedure = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

# If you intend to use ProjectView, uncomment and define it:
# class ProjectView(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)





