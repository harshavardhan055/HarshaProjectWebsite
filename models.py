from slugify import slugify
from your_flask_app import db  # Adjust import as needed

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    profile_photo = db.Column(db.String(256), nullable=True)  # Add profile photo path

    # Add any other fields you have here


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Add paths or content fields as needed, for example:
    image_path = db.Column(db.String(256))
    video_path = db.Column(db.String(256))
    circuit_diagram = db.Column(db.String(256))
    code = db.Column(db.Text)
    description = db.Column(db.Text)
    # Add other fields as needed

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.slug and self.title:
            self.slug = slugify(self.title)


class Testing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Similar fields as Project
    image_path = db.Column(db.String(256))
    video_path = db.Column(db.String(256))
    circuit_diagram = db.Column(db.String(256))
    code = db.Column(db.Text)
    description = db.Column(db.Text)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.slug and self.title:
            self.slug = slugify(self.title)


