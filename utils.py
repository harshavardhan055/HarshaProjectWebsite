import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    """Check if a filename has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file, folder):
    """Save an uploaded file to a specific folder within UPLOAD_FOLDER
    
    Args:
        file: The file from the request
        folder: Subfolder name within UPLOAD_FOLDER
        
    Returns:
        The relative path to the saved file or None if no file was saved
    """
    if not file or file.filename == '':
        return None
        
    if file and allowed_file(file.filename):
        # Generate a unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Create folder if it doesn't exist
        folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(folder_path, unique_filename)
        file.save(file_path)
        
        # Return the relative path for database storage
        return os.path.join('uploads', folder, unique_filename)
    
    return None

def delete_file(filepath):
    """Delete a file from the filesystem
    
    Args:
        filepath: The relative path to the file (stored in the database)
    """
    if not filepath:
        return
        
    # Convert relative path to absolute path
    absolute_path = os.path.join(current_app.root_path, 'static', filepath)
    
    try:
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
    except Exception as e:
        current_app.logger.error(f"Error deleting file {absolute_path}: {e}")

def is_admin_ip(ip_address):
    """Check if the IP address is allowed for admin access"""
    # Allow all IPs for now - in production you might want to restrict this
    return True
