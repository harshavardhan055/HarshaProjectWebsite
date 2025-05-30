import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db, Project, Testing
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

main_routes = Blueprint("main_routes", __name__)

# Allowed file extensions for admin upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'pdf', 'py', 'c', 'ino', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------- Home ----------------------

@main_routes.route("/")
def home():
    return render_template("index.html")

# ---------------------- Login ----------------------

@main_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("main_routes.home"))
        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html")

# ---------------------- Logout ----------------------

@main_routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("main_routes.home"))

# ---------------------- Register ----------------------

@main_routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        confirm_password = request.form.get("confirm_password").strip()

        if not username or not email or not password or not confirm_password:
            flash("Please fill in all fields.", "warning")
            return redirect(url_for("main_routes.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("main_routes.register"))

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
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

# ---------------------- Projects (List + Search) ----------------------

@main_routes.route("/projects")
@login_required
def projects():
    query = request.args.get("q", "")
    all_projects = Project.query.filter(Project.title.ilike(f"%{query}%")).all()
    return render_template("projects.html", projects=all_projects, query=query)

# ---------------------- Testing (List + Search) ----------------------

@main_routes.route("/testing")
@login_required
def testing():
    query = request.args.get("q", "")
    all_testings = Testing.query.filter(Testing.title.ilike(f"%{query}%")).all()
    return render_template("testing.html", testings=all_testings, query=query)

# ---------------------- Project Detail View ----------------------

@main_routes.route("/projects/<project_name>")
@login_required
def project_detail(project_name):
    project = Project.query.filter_by(title=project_name).first_or_404()
    base_path = os.path.join("uploads", "projects", project_name)
    static_path = os.path.join(current_app.static_folder, base_path)

    def get_files(file_type):
        folder = os.path.join(static_path, file_type)
        if os.path.exists(folder):
            return [os.path.join(base_path, file_type, f) for f in os.listdir(folder)]
        return []

    return render_template(
        "project_detail.html",
        item_name=project_name,
        image_files=get_files("image"),
        video_files=get_files("video"),
        code_files=get_files("code"),
        description_files=get_files("description"),
        circuit_files=get_files("circuitdiagram")
    )

# ---------------------- Testing Detail View ----------------------

@main_routes.route("/testing/<testing_name>")
@login_required
def testing_detail(testing_name):
    testing = Testing.query.filter_by(title=testing_name).first_or_404()
    base_path = os.path.join("uploads", "testing", testing_name)
    static_path = os.path.join(current_app.static_folder, base_path)

    def get_files(file_type):
        folder = os.path.join(static_path, file_type)
        if os.path.exists(folder):
            return [os.path.join(base_path, file_type, f) for f in os.listdir(folder)]
        return []

    return render_template(
        "testing_detail.html",
        item_name=testing_name,
        image_files=get_files("image"),
        video_files=get_files("video"),
        code_files=get_files("code"),
        description_files=get_files("description"),
        circuit_files=get_files("circuitdiagram")
    )

# ---------------------- Admin Dashboard ----------------------

@main_routes.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for("main_routes.home"))
    return render_template("admin/dashboard.html")

# ---------------------- Admin Upload ----------------------

@main_routes.route("/admin/upload", methods=["POST"])
@login_required
def upload_file():
    if not current_user.is_admin:
        flash("Access denied: Admins only.", "danger")
        return redirect(url_for("main_routes.home"))

    file = request.files.get("file")
    item_name = request.form.get("item_name", "").strip()
    file_type = request.form.get("file_type", "").strip().lower()
    category = request.form.get("category", "").strip().lower()

    if not item_name or not file_type or category not in ['projects', 'testing']:
        flash("Missing required fields.", "danger")
        return redirect(url_for("main_routes.admin_dashboard"))

    # Create or fetch entry
    item = Project.query.filter_by(title=item_name).first() if category == 'projects' else Testing.query.filter_by(title=item_name).first()
    if not item:
        item = Project(title=item_name, user_id=current_user.id) if category == 'projects' else Testing(title=item_name, user_id=current_user.id)
        db.session.add(item)

    # Save file
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.root_path, "static", "uploads", category, item_name, file_type)
        os.makedirs(upload_path, exist_ok=True)
        full_path = os.path.join(upload_path, filename)
        file.save(full_path)

        path = f"uploads/{category}/{item_name}/{file_type}/{filename}"
        if file_type == "image":
            item.image_path = path
        elif file_type == "video":
            item.video_path = path
        elif file_type == "circuitdiagram":
            item.circuit_diagram = path
        elif file_type == "code":
            item.code = open(full_path, "r", encoding="utf-8", errors="ignore").read()
        elif file_type == "description":
            item.description = open(full_path, "r", encoding="utf-8", errors="ignore").read()
        elif file_type == "connections":
            item.connections = open(full_path, "r", encoding="utf-8", errors="ignore").read()
        elif file_type == "procedure":
            item.procedure = open(full_path, "r", encoding="utf-8", errors="ignore").read()

    db.session.commit()
    flash(f"{file_type.capitalize()} uploaded and saved for '{item_name}'", "success")
    return redirect(url_for("main_routes.admin_dashboard"))

# ---------------------- Profile ----------------------

@main_routes.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

# ---------------------- Contact ----------------------

@main_routes.route("/contact")
def contact():
    return render_template("contact.html")



