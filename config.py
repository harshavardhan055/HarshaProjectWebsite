import os

# A strong, random secret key for Flask sessions and security
# IMPORTANT: In a production environment, this should be set via environment variables
# For Render, you can set it as an environment variable in the service settings.
# Example: SECRET_KEY = os.environ.get('SECRET_KEY', 'your_super_secret_key_that_you_change_for_production')
SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_and_random_string_here_change_me_in_production'

# Database configuration
# For SQLite, the path will be relative to the application's root path on Render
SQLALCHEMY_DATABASE_URI = 'sqlite:///harsha_projects.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Upload folder configuration (relative to static directory)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'pdf', 'py', 'c', 'ino', 'txt'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB limit
