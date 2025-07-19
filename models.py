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

    projects = db.relationship("Project", backref="owner", lazy=True)
    testings = db.relationship("Testing", backref="owner", lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Uploaded file paths (stored as strings)
    image_filename = db.Column(db.String(255))
    code_filename = db.Column(db.String(255))
    video_filename = db.Column(db.String(255))
    diagram_filename = db.Column(db.String(255))
    text_filename = db.Column(db.String(255))  # project info / procedure text

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
    text_filename = db.Column(db.String(255))  # testing notes / result summary

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    email = db.Column(db.String(150))
    about = db.Column(db.Text)  # new field
    profile_photo = db.Column(db.String(300))  # path to profile image

    # Assume project history is tracked via another table or a relationship
    project_views = db.relationship('ProjectView', backref='user', lazy=True)




