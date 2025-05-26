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

@main_routes.route("/admin/upload", methods=["POST"])
@login_required
def upload_file():
    if not current_user.is_admin:
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for("main_routes.home"))

    file = request.files.get("file")
    item_name = request.form.get("item_name", "").strip()
    file_type = request.form.get("file_type", "").strip().lower()
    category = request.form.get("category", "").strip().lower()  # 'projects' or 'testing'

    if not file or file.filename == "":
        flash("No file selected.", "warning")
        return redirect(url_for("main_routes.admin_dashboard"))

    if not allowed_file(file.filename):
        flash("File type not allowed.", "danger")
        return redirect(url_for("main_routes.admin_dashboard"))

    if not item_name or not file_type or category not in ['projects', 'testing']:
        flash("Missing required fields.", "danger")
        return redirect(url_for("main_routes.admin_dashboard"))

    filename = secure_filename(file.filename)
    upload_path = os.path.join(current_app.root_path, "static", "uploads", category, item_name, file_type)
    os.makedirs(upload_path, exist_ok=True)
    file.save(os.path.join(upload_path, filename))

    flash(f"{file_type.capitalize()} uploaded successfully under '{item_name}'.", "success")
    return redirect(url_for("main_routes.admin_dashboard"))

@main_routes.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@main_routes.route("/contact")
def contact():
    return render_template("contact.html")

