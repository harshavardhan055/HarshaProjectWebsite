import os
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db, Project, Testing
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from slugify import slugify

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


def get_files_for_item(base_static_path, base_path, file_type):
    folder = os.path.join(base_static_path, file_type)
    if os.path.exists(folder) and os.path.isdir(folder):
        return [
            os.path.join(base_path, file_type, f)
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
        ]
    return []


# Fix project_detail and testing_detail to use slug instead of title

@main_routes.route("/projects/<slug>")
@login_required
def project_detail(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    base_path = os.path.join("uploads", "projects", project.slug)
    static_path = os.path.join(current_app.static_folder, base_path)

    return render_template(
        "project_detail.html",
        item_name=project.title,
        image_files=get_files_for_item(static_path, base_path, "image"),
        video_files=get_files_for_item(static_path, base_path, "video"),
        code_files=get_files_for_item(static_path, base_path, "code"),
        description_files=get_files_for_item(static_path, base_path, "description"),
        circuit_files=get_files_for_item(static_path, base_path, "circuitdiagram"),
    )


@main_routes.route("/testing/<slug>")
@login_required
def testing_detail(slug):
    testing = Testing.query.filter_by(slug=slug).first_or_404()
    base_path = os.path.join("uploads", "testing", testing.slug)
    static_path = os.path.join(current_app.static_folder, base_path)

    return render_template(
        "testing_detail.html",
        item_name=testing.title,
        image_files=get_files_for_item(static_path, base_path, "image"),
        video_files=get_files_for_item(static_path, base_path, "video"),
        code_files=get_files_for_item(static_path, base_path, "code"),
        description_files=get_files_for_item(static_path, base_path, "description"),
        circuit_files=get_files_for_item(static_path, base_path, "circuitdiagram"),
    )


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
    category = request.form.get("category", "").strip().lower()

    if not item_name or not file_type or category not in ['projects', 'testing']:
        flash("Missing or invalid required fields.", "danger")
        return redirect(url_for("main_routes.admin_dashboard"))

    if not file or file.filename == "":
        flash("No file selected for uploading.", "warning")
        return redirect(url_for("main_routes.admin_dashboard"))

    if not allowed_file(file.filename):
        flash("File type not allowed.", "danger")
        return redirect(url_for("main_routes.admin_dashboard"))

    # Find or create item by slug now
    item = None
    slug = slugify(item_name)

    if category == 'projects':
        item = Project.query.filter_by(slug=slug).first()
        if not item:
            item = Project(title=item_name, slug=slug, user_id=current_user.id)
            db.session.add(item)
    else:  # testing
        item = Testing.query.filter_by(slug=slug).first()
        if not item:
            item = Testing(title=item_name, slug=slug, user_id=current_user.id)
            db.session.add(item)

    filename = secure_filename(file.filename)
    upload_path = os.path.join(current_app.root_path, "static", "uploads", category, slug, file_type)
    os.makedirs(upload_path, exist_ok=True)
    full_path = os.path.join(upload_path, filename)

    try:
        file.save(full_path)
    except Exception as e:
        flash(f"Failed to save file: {str(e)}", "danger")
        return redirect(url_for("main_routes.admin_dashboard"))

    relative_path = f"uploads/{category}/{slug}/{file_type}/{filename}"

    if file_type == "image":
        item.image_path = relative_path
    elif file_type == "video":
        item.video_path = relative_path
    elif file_type == "circuitdiagram":
        item.circuit_diagram = relative_path
    elif file_type in {"code", "description", "connections", "procedure"}:
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            setattr(item, file_type, content)
        except Exception as e:
            flash(f"Failed to read {file_type} file: {str(e)}", "danger")
            return redirect(url_for("main_routes.admin_dashboard"))
    else:
        flash("Unknown file type.", "warning")

    db.session.commit()
    flash(f"{file_type.capitalize()} uploaded and saved for '{item_name}'.", "success")
    return redirect(url_for("main_routes.admin_dashboard"))


@main_routes.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@main_routes.route("/profile/upload_photo", methods=["POST"])
@login_required
def upload_profile_photo():
    file = request.files.get("photo")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, "static", "uploads", "profile_photos")
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        current_user.profile_photo = f"uploads/profile_photos/{filename}"
        db.session.commit()
        flash("Profile photo updated.", "success")
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
    return render_template("500.html"), 500
