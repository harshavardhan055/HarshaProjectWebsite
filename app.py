from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)

# Replace this with a secure secret key in production (set via environment variable ideally)
app.secret_key = os.environ.get('SECRET_KEY', 'a-secure-dev-key')

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================== MODELS ==================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ================== ROUTES ==================
@app.route("/")
def home():
    return render_template("home.html", current_year=datetime.now().year)

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Logged in successfully!", "success")
            return redirect(url_for('profile'))
        flash('Invalid credentials', 'danger')
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash("Email already registered", 'warning')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please log in.", 'success')
        return redirect(url_for('login'))

    return render_template("register.html")

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", 'warning')
        return redirect(url_for('logout'))

    return render_template("profile.html", user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        db.session.commit()
        flash("Profile updated!", 'success')
        return redirect(url_for('profile'))

    return render_template("edit_profile.html", user=user)

@app.route('/projects')
def projects():
    projects = Project.query.all()
    return render_template("projects.html", projects=projects)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template("project_detail.html", project=project)

@app.route('/testing')
def testing():
    return render_template("testing.html")

@app.route('/testing/<int:test_id>')
def testing_detail(test_id):
    return render_template("testing_detail.html", test_id=test_id)

@app.route('/search')
def search_results():
    query = request.args.get("query", "")
    results = Project.query.filter(Project.title.contains(query)).all()
    return render_template("search_results.html", results=results, query=query)

@app.route('/verify')
def verify_email():
    return render_template("verify_email.html")

# ================== ERROR HANDLERS ==================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# ================== INIT APP ==================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database initialized.")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
