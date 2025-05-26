import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

main_routes = Blueprint("main_routes", __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'pdf', 'py', 'c', 'ino', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_routes.route("/")
def home():
    return render_template("index.html")

@main_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("main_routes.home"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")

@main_routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("main_routes.home"))

@main_routes.route("/register", methods=["GET", "POST"])
def register():
    # Implement registration logic here (form handling, validation, create user, etc.)
    return render_template("register.html")

@main_routes.route("/projects")
@login_required
def projects():
    return render_template("projects.html")

@main_routes.route("/testing")
@login_required
def testing():
    return render_template("testing.html")

@main_routes.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for("main_routes.home"))
    return render_template("admin/dashboard.html")

@main_routes.route("/admin/upload", methods=["GET", "POST"])
@login_required
def admin_upload_file():
    # Only allow admin users to access upload
    if not current_user.is_admin:
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for("main_routes.home"))

    if request.method == "POST":
        if 'file' not in request.files:
            flash("No file part", "warning")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash("No selected file", "warning")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))
            flash("File uploaded successfully!", "success")
            return redirect(url_for("main_routes.admin_upload_file"))
        else:
            flash("File type not allowed.", "danger")
            return redirect(request.url)

    return render_template("admin/upload.html")

@main_routes.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@main_routes.route("/contact")
def contact():
    return render_template("contact.html")
