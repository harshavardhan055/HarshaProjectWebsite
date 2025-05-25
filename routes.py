from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from werkzeug.security import check_password_hash
from forms import LoginForm, RegisterForm  # Import your form classes

main_routes = Blueprint("main_routes", __name__)

@main_routes.route("/")
def home():
    return render_template("index.html")

@main_routes.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("main_routes.home"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

@main_routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("main_routes.home"))

@main_routes.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Registration logic (example)
        # new_user = User(username=form.username.data, ...)
        # new_user.set_password(form.password.data)  # your user model method
        # db.session.add(new_user)
        # db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("main_routes.login"))
    return render_template("register.html", form=form)

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

@main_routes.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@main_routes.route("/contact")
def contact():
    return render_template("contact.html")

