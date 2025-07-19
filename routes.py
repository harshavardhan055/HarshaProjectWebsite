import os
import re
from datetime import datetime
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, current_app, send_from_directory
)
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db, Project, Testing # Import db from app_init, not app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from utils import allowed_file, save_uploaded_file, delete_file # Import from utils

main_routes = Blueprint("main_routes", __name__)

# ALLOWED_EXTENSIONS is now read from app.config (defined in config.py)

def custom_slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

@main_routes.route("/about")
def about():
    """Render the about page."""
    return render_template("about.html", title="About Harsha's Projects")

@main_routes.route("/")
def home():
    return render_template("index.html")

@main_routes.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main_routes.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.", "warning")
            return redirect(url_for("main_routes.login"))

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("main_routes.home"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")

@main_routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("main_routes.home"))

@main_routes.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main_routes.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not username or not email or not password or not confirm_password:
            flash("Please fill in all fields.", "warning")
            return redirect(url_for("main_routes.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("main_routes.register"))

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username or email already exists.", "danger")
            return redirect(url_for("main_routes.register"))

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=False
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("main_routes.login"))

    return render_template("register.html")

@main_routes.route("/projects")
@login_required
def projects():
    query = request.args.get("q", "")
    projects = Project.query.filter(Project.title.ilike(f"%{query}%")).all()
    return render_template("projects.html", projects=projects, query=query)

@main_routes.route("/testing")
@login_required
def testing():
    query = request.args.get("q", "")
    testings = Testing.query.filter(Testing.title.ilike(f"%{query}%")).all()
    return render_template("testing.html", testings=testings, query=query)

def get_files_for_item_display(item_object, base_upload_folder):
    """
    Constructs a dictionary of file paths for display based on item object's stored paths.
    """
    files_dict = {
        "image_files": [],
        "video_files": [],
        "code_files": [],
        "description_files": [],
        "circuit_files": []
    }

    if item_object.image_path:
        files_dict["image_files"].append(url_for('static', filename=item_object.image_path))
    if item_object.video_path:
        files_dict["video_files"].append(url_for('static', filename=item_object.video_path))
    if item_object.circuit_diagram_path:
        files_dict["circuit_files"].append(url_for('static', filename=item_object.circuit_diagram_path))

    # For text content directly stored in DB, we don't have separate files to list.
    # The content itself will be passed to the template.
    return files_dict

@main_routes.route("/projects/<slug>")
@login_required
def project_detail(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    
    # Files are now handled directly via model paths if they are single files
    # For content (code, description, etc.), the content is directly in the model
    return render_template(
        "project_detail.html",
        item=project, # Pass the whole item object
        image_url=url_for('static', filename=project.image_path) if project.image_path else None,
        video_url=url_for('static', filename=project.video_path) if project.video_path else None,
        circuit_diagram_url=url_for('static', filename=project.circuit_diagram_path) if project.circuit_diagram_path else None
    )

@main_routes.route("/testing/<slug>")
@login_required
def testing_detail(slug):
    testing_item = Testing.query.filter_by(slug=slug).first_or_404()

    return render_template(
        "testing_detail.html",
        item=testing_item, # Pass the whole item object
        image_url=url_for('static', filename=testing_item.image_path) if testing_item.image_path else None,
        video_url=url_for('static', filename=testing_item.video_path) if testing_item.video_path else None,
        circuit_diagram_url=url_for('static', filename=testing_item.circuit_diagram_path) if testing_item.circuit_diagram_path else None
    )

@main_routes.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for("main_routes.home"))
    
    projects = Project.query.all()
    testings = Testing.query.all()
    
    return render_template("admin/dashboard.html", projects=projects, testings=testings)

@main_routes.route("/admin/upload", methods=["POST"])
@login_required
def upload_file():
    if not current_user.is_admin:
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for("main_routes.home"))

    item_name = request.form.get("item_name", "").strip()
    file_type = request.form.get("file_type", "").strip().lower() # e.g., 'image', 'code', 'description'
    category = request.form.get("category", "").strip().lower() # 'projects' or 'testing'

    if not item_name or not file_type or category not in ['projects', 'testing']:
        flash("Missing or invalid required fields (Item Name, File Type, Category).", "danger")
        return redirect(url_for("main_routes.admin_dashboard"))

    slug = custom_slugify(item_name)

    if category == 'projects':
        item = Project.query.filter_by(slug=slug).first()
        if not item:
            item = Project(title=item_name, slug=slug, user_id=current_user.id)
            db.session.add(item)
            db.session.commit() # Commit to get an ID for the new item
    else: # category == 'testing'
        item = Testing.query.filter_by(slug=slug).first()
        if not item:
            item = Testing(title=item_name, slug=slug, user_id=current_user.id)
            db.session.add(item)
            db.session.commit() # Commit to get an ID for the new item

    # Handle file uploads (image, video, circuitdiagram)
    if file_type in {"image", "video", "circuitdiagram"}:
        file = request.files.get("file")
        if not file or file.filename == "":
            flash(f"No file selected for {file_type}.", "warning")
            return redirect(url_for("main_routes.admin_dashboard"))

        if not allowed_file(file.filename):
            flash(f"File type for {file_type} not allowed.", "danger")
            return redirect(url_for("main_routes.admin_dashboard"))

        # Save to static/uploads/category/slug/file_type/
        upload_folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], category, slug, file_type)
        os.makedirs(upload_folder_path, exist_ok=True)
        
        filename = secure_filename(file.filename)
        file_path_full = os.path.join(upload_folder_path, filename)
        
        try:
            file.save(file_path_full)
            relative_path_for_db = os.path.join(current_app.config['UPLOAD_FOLDER'], category, slug, file_type, filename).replace(os.sep, '/')
            
            if file_type == "image":
                item.image_path = relative_path_for_db
            elif file_type == "video":
                item.video_path = relative_path_for_db
            elif file_type == "circuitdiagram":
                item.circuit_diagram_path = relative_path_for_db
            
            db.session.commit()
            flash(f"{file_type.capitalize()} uploaded and saved for '{item_name}'.", "success")

        except Exception as e:
            flash(f"Failed to save {file_type} file: {str(e)}", "danger")

    # Handle text content (code, description, connections, procedure)
    elif file_type in {"code", "description", "connections", "procedure"}:
        # Check if text content is directly provided via a textarea (assuming this)
        content = request.form.get("text_content") # New form field for text content
        if not content:
            flash(f"No text content provided for {file_type}.", "warning")
            return redirect(url_for("main_routes.admin_dashboard"))
        
        try:
            setattr(item, file_type, content) # Directly set the content to the model field
            db.session.commit()
            flash(f"{file_type.capitalize()} content saved for '{item_name}'.", "success")
        except Exception as e:
            flash(f"Failed to save {file_type} content: {str(e)}", "danger")
    else:
        flash("Unknown file type or content type.", "warning")

    return redirect(url_for("main_routes.admin_dashboard"))

@main_routes.route("/admin/delete_item/<category>/<int:item_id>", methods=["POST"])
@login_required
def delete_item(category, item_id):
    if not current_user.is_admin:
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for("main_routes.home"))

    item = None
    if category == 'projects':
        item = Project.query.get(item_id)
    elif category == 'testing':
        item = Testing.query.get(item_id)

    if not item:
        flash("Item not found.", "danger")
        return redirect(url_for("main_routes.admin_dashboard"))

    try:
        # Delete associated files from the filesystem
        # Construct the base directory for the item's uploads
        item_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], category, item.slug)
        if os.path.exists(item_upload_dir):
            import shutil
            shutil.rmtree(item_upload_dir) # Remove the entire directory for the item's uploads
            current_app.logger.info(f"Deleted directory: {item_upload_dir}")

        db.session.delete(item)
        db.session.commit()
        flash(f"{category.capitalize()} '{item.title}' deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting {category} '{item.title}': {str(e)}", "danger")
    
    return redirect(url_for("main_routes.admin_dashboard"))


@main_routes.route("/profile")
@login_required
def profile():
    return render_template(
        "profile.html",
        user=current_user,
        # project_history=current_user.project_views if hasattr(current_user, "project_views") else [] # Uncomment if ProjectView is used
    )

@main_routes.route("/profile/upload_photo", methods=["POST"])
@login_required
def upload_profile_photo():
    file = request.files.get("photo")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{current_user.id}_{timestamp}_{filename}"

        upload_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], "profile_photos")
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        current_user.profile_photo = os.path.join(current_app.config['UPLOAD_FOLDER'], "profile_photos", unique_filename).replace(os.sep, '/')
        db.session.commit()

        flash("Profile photo updated successfully.", "success")
    else:
        flash("Invalid file or no file selected.", "danger")

    return redirect(url_for("main_routes.profile"))

@main_routes.route("/contact")
def contact():
    return render_template("contact.html")

@main_routes.app_errorhandler(403)
def forbidden_error(error):
    return render_template("403.html"), 403

@main_routes.app_errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404

@main_routes.app_errorhandler(500)
def internal_error(error):
    db.session.rollback() # Rollback in case of database errors
    return render_template("500.html"), 500
