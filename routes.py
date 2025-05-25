from flask import Blueprint, render_template

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def home():
    return render_template('home.html')

@main_routes.route('/login')
def login():
    return render_template('login.html')

# Add other routes as needed

