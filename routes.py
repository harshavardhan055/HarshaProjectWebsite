from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from werkzeug.security import check_password_hash

main_routes = Blueprint("main_routes", __name__)

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

@main_routes.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)
