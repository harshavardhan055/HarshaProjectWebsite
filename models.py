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

    projects = db.relationship('Project', backref='author', lazy='dynamic')
    testing_items = db.relationship('Testing', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Upload status flags
    image_uploaded = db.Column(db.Boolean, default=False)
    code_uploaded = db.Column(db.Boolean, default=False)
    circuit_diagram_uploaded = db.Column(db.Boolean, default=False)
    video_uploaded = db.Column(db.Boolean, default=False)
    description_uploaded = db.Column(db.Boolean, default=False)
    connections_uploaded = db.Column(db.Boolean, default=False)
    procedure_uploaded = db.Column(db.Boolean, default=False)

    folder_path = db.Column(db.String(256))  # static/uploads/projects/<title>/
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Project {self.title}>'

class Testing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Upload status flags
    image_uploaded = db.Column(db.Boolean, default=False)
    code_uploaded = db.Column(db.Boolean, default=False)
    circuit_diagram_uploaded = db.Column(db.Boolean, default=False)
    video_uploaded = db.Column(db.Boolean, default=False)
    description_uploaded = db.Column(db.Boolean, default=False)
    connections_uploaded = db.Column(db.Boolean, default=False)
    procedure_uploaded = db.Column(db.Boolean, default=False)

    folder_path = db.Column(db.String(256))  # static/uploads/testing/<title>/
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Testing {self.title}>'   check this models.py 

