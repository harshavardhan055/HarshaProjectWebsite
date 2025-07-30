from datetime import datetime, timedelta
from flask_login import UserMixin
from extensions import db  # ✅ This is important

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    profile_photo = db.Column(db.String(256))
    interests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship('Project', backref='author', lazy='dynamic')
    testing_items = db.relationship('Testing', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(256))
    code = db.Column(db.Text)
    video_path = db.Column(db.String(256))
    circuit_diagram = db.Column(db.String(256))
    connections = db.Column(db.Text)
    procedure = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Project {self.title}>'

class Testing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(256))
    code = db.Column(db.Text)
    video_path = db.Column(db.String(256))
    circuit_diagram = db.Column(db.String(256))
    connections = db.Column(db.Text)
    procedure = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Testing {self.title}>'

class EmailVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_used = db.Column(db.Boolean, default=False)

    def is_expired(self):
        return datetime.utcnow() - self.created_at > timedelta(minutes=10)

    def __repr__(self):
        return f'<EmailVerification {self.email}>'

class ProjectComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    user = db.relationship('User', backref='project_comments')
    project = db.relationship('Project', backref='comments')

    def __repr__(self):
        return f'<ProjectComment {self.id}>'

class ProjectRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    user = db.relationship('User', backref='project_ratings')
    project = db.relationship('Project', backref='ratings')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'project_id', name='unique_user_project_rating'),
    )

    def __repr__(self):
        return f'<ProjectRating {self.rating} stars for project {self.project_id}>'

class SocialMediaLinks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    youtube_url = db.Column(db.String(256), default='')
    instagram_url = db.Column(db.String(256), default='')
    github_url = db.Column(db.String(256), default='')
    linkedin_url = db.Column(db.String(256), default='')
    twitter_url = db.Column(db.String(256), default='')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SocialMediaLinks {self.id}>'
