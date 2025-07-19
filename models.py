from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Optional fields from second definition
    about = db.Column(db.Text)
    profile_photo = db.Column(db.String(300))

    # Relationships
    projects = db.relationship("Project", backref="owner", lazy=True)
    testings = db.relationship("Testing", backref="owner", lazy=True)
    project_views = db.relationship("ProjectView", backref="user", lazy=True)  # If defined elsewhere

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Uploaded file paths
    image_filename = db.Column(db.String(255))
    code_filename = db.Column(db.String(255))
    video_filename = db.Column(db.String(255))
    diagram_filename = db.Column(db.String(255))
    text_filename = db.Column(db.String(255))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Testing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    image_filename = db.Column(db.String(255))
    code_filename = db.Column(db.String(255))
    video_filename = db.Column(db.String(255))
    diagram_filename = db.Column(db.String(255))
    text_filename = db.Column(db.String(255))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

# Optional: define ProjectView only if needed
# class ProjectView(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)





