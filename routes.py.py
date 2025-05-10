import os
from flask import render_template, flash, redirect, url_for, request, abort, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Project, Testing
from forms import LoginForm, RegistrationForm, ProjectForm, TestingForm
from utils import save_uploaded_file, delete_file, is_admin_ip

@app.route('/')
def index():
    # Get 3 featured projects for the homepage
    featured_projects = Project.query.order_by(Project.created_at.desc()).limit(3).all()
    return render_template('home.html', featured_projects=featured_projects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not check_password_hash(user.password_hash, form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
        
        flash('Login successful!', 'success')
        return redirect(next_page)
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Project routes
@app.route('/projects')
@login_required
def projects():
    all_projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=all_projects)

@app.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)

# Testing routes
@app.route('/testing')
@login_required
def testing():
    all_testing = Testing.query.order_by(Testing.created_at.desc()).all()
    return render_template('testing.html', testing_items=all_testing)

@app.route('/testing/<int:testing_id>')
@login_required
def testing_detail(testing_id):
    testing_item = Testing.query.get_or_404(testing_id)
    return render_template('testing_detail.html', testing=testing_item)

# Admin routes
def admin_required(func):
    def decorated_function(*args, **kwargs):
        # Check if user is logged in and is admin
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        
        # Check if request comes from allowed IP for extra security
        client_ip = request.remote_addr
        if not is_admin_ip(client_ip):
            app.logger.warning(f"Admin access attempted from unauthorized IP: {client_ip}")
            abort(403)  # Forbidden
            
        return func(*args, **kwargs)
    
    # Make sure decorated function has the same name and attributes as the original
    decorated_function.__name__ = func.__name__
    return login_required(decorated_function)

@app.route('/admin')
@admin_required
def admin_dashboard():
    projects = Project.query.all()
    testing_items = Testing.query.all()
    return render_template('admin/dashboard.html', projects=projects, testing_items=testing_items)

@app.route('/admin/add-project', methods=['GET', 'POST'])
@admin_required
def add_project():
    form = ProjectForm()
    
    if form.validate_on_submit():
        # Save uploaded files
        image_path = save_uploaded_file(form.image.data, 'projects/images')
        video_path = save_uploaded_file(form.video.data, 'projects/videos')
        circuit_path = save_uploaded_file(form.circuit_diagram.data, 'projects/circuits')
        
        # Create new project
        project = Project(
            title=form.title.data,
            description=form.description.data,
            image_path=image_path,
            code=form.code.data,
            video_path=video_path,
            circuit_diagram=circuit_path,
            connections=form.connections.data,
            procedure=form.procedure.data,
            user_id=current_user.id
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('Project added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/add_project.html', form=form)

@app.route('/admin/edit-project/<int:project_id>', methods=['GET', 'POST'])
@admin_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        # Handle file uploads - only update if new file is provided
        if form.image.data:
            if project.image_path:
                delete_file(project.image_path)
            project.image_path = save_uploaded_file(form.image.data, 'projects/images')
            
        if form.video.data:
            if project.video_path:
                delete_file(project.video_path)
            project.video_path = save_uploaded_file(form.video.data, 'projects/videos')
            
        if form.circuit_diagram.data:
            if project.circuit_diagram:
                delete_file(project.circuit_diagram)
            project.circuit_diagram = save_uploaded_file(form.circuit_diagram.data, 'projects/circuits')
        
        # Update text fields
        project.title = form.title.data
        project.description = form.description.data
        project.code = form.code.data
        project.connections = form.connections.data
        project.procedure = form.procedure.data
        
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_project.html', form=form, project=project)

@app.route('/admin/delete-project/<int:project_id>')
@admin_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Delete associated files
    if project.image_path:
        delete_file(project.image_path)
    if project.video_path:
        delete_file(project.video_path)
    if project.circuit_diagram:
        delete_file(project.circuit_diagram)
    
    # Delete from database
    db.session.delete(project)
    db.session.commit()
    
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add-testing', methods=['GET', 'POST'])
@admin_required
def add_testing():
    form = TestingForm()
    
    if form.validate_on_submit():
        # Save uploaded files
        image_path = save_uploaded_file(form.image.data, 'testing/images')
        video_path = save_uploaded_file(form.video.data, 'testing/videos')
        circuit_path = save_uploaded_file(form.circuit_diagram.data, 'testing/circuits')
        
        # Create new testing item
        testing = Testing(
            title=form.title.data,
            description=form.description.data,
            image_path=image_path,
            code=form.code.data,
            video_path=video_path,
            circuit_diagram=circuit_path,
            connections=form.connections.data,
            procedure=form.procedure.data,
            user_id=current_user.id
        )
        
        db.session.add(testing)
        db.session.commit()
        
        flash('Testing item added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/add_testing.html', form=form)

@app.route('/admin/edit-testing/<int:testing_id>', methods=['GET', 'POST'])
@admin_required
def edit_testing(testing_id):
    testing = Testing.query.get_or_404(testing_id)
    form = TestingForm(obj=testing)
    
    if form.validate_on_submit():
        # Handle file uploads - only update if new file is provided
        if form.image.data:
            if testing.image_path:
                delete_file(testing.image_path)
            testing.image_path = save_uploaded_file(form.image.data, 'testing/images')
            
        if form.video.data:
            if testing.video_path:
                delete_file(testing.video_path)
            testing.video_path = save_uploaded_file(form.video.data, 'testing/videos')
            
        if form.circuit_diagram.data:
            if testing.circuit_diagram:
                delete_file(testing.circuit_diagram)
            testing.circuit_diagram = save_uploaded_file(form.circuit_diagram.data, 'testing/circuits')
        
        # Update text fields
        testing.title = form.title.data
        testing.description = form.description.data
        testing.code = form.code.data
        testing.connections = form.connections.data
        testing.procedure = form.procedure.data
        
        db.session.commit()
        flash('Testing item updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_testing.html', form=form, testing=testing)

@app.route('/admin/delete-testing/<int:testing_id>')
@admin_required
def delete_testing(testing_id):
    testing = Testing.query.get_or_404(testing_id)
    
    # Delete associated files
    if testing.image_path:
        delete_file(testing.image_path)
    if testing.video_path:
        delete_file(testing.video_path)
    if testing.circuit_diagram:
        delete_file(testing.circuit_diagram)
    
    # Delete from database
    db.session.delete(testing)
    db.session.commit()
    
    flash('Testing item deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
