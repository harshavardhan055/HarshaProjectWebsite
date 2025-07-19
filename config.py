import os

# Secret key for session management (IMPORTANT: Change this to a strong, random value in production)
SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-this-secret-key'

# Database configuration
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'harsha_projects.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# File upload configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads') # Files will be saved in the static/uploads directory
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'pdf', 'py', 'c', 'ino', 'txt', 'zip', 'rar'} # Added zip, rar for code/description zips
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit for uploads
