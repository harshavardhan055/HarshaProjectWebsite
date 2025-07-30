from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from functools import wraps
import os

from app import app, db
from models import Project, Contact, SocialMediaLinks
from forms import ProjectForm, SocialMediaForm
from utils import save_uploaded_file, delete_file
@app.context_processor
def inject_social_media():
    """Make social media links available in all templates"""
    social_media = SocialMediaLinks.query.first()
    return dict(social_media=social_media)

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
        # Store registration data in session
        session['registration_data'] = {
            'username': form.username.data,
            'email': form.email.data,
            'password': form.password.data,
            'interests': ','.join(form.interests.data)
        }
        
        # Send verification email
        if create_verification_record(form.email.data):
            flash('Verification code sent to your email. Please check your email and enter the code.', 'info')
            return redirect(url_for('verify_email'))
        else:
            flash('Error sending verification email. Please try again.', 'danger')
    
    return render_template('register.html', form=form)

@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if 'registration_data' not in session:
        flash('No registration data found. Please register again.', 'danger')
        return redirect(url_for('register'))
    
    form = EmailVerificationForm()
    form.email.data = session['registration_data']['email']
    
    if form.validate_on_submit():
        if verify_otp(form.email.data, form.otp.data):
            # Create the user account
            reg_data = session['registration_data']
            user = User(
                username=reg_data['username'],
                email=reg_data['email'],
                password_hash=generate_password_hash(reg_data['password']),
                interests=reg_data['interests'],
                is_verified=True
            )
            db.session.add(user)
            db.session.commit()
            
            # Clear session data
            session.pop('registration_data', None)
            
            flash('Email verified successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid or expired verification code. Please try again.', 'danger')
    
    return render_template('verify_email.html', form=form, email=session['registration_data']['email'])

@app.route('/resend-verification')
def resend_verification():
    if 'registration_data' not in session:
        flash('No registration data found. Please register again.', 'danger')
        return redirect(url_for('register'))
    
    email = session['registration_data']['email']
    if create_verification_record(email):
        flash('Verification code resent to your email.', 'info')
    else:
        flash('Error sending verification email. Please try again.', 'danger')
    
    return redirect(url_for('verify_email'))

@app.route('/search')
@login_required
def search():
    form = SearchForm()
    projects = []
    testing_items = []
    query = request.args.get('query', '')
    
    if query:
        # Search in projects
        projects = Project.query.filter(
            or_(
                Project.title.contains(query),
                Project.description.contains(query),
                Project.code.contains(query),
                Project.connections.contains(query),
                Project.procedure.contains(query)
            )
        ).all()
        
        # Search in testing items
        testing_items = Testing.query.filter(
            or_(
                Testing.title.contains(query),
                Testing.description.contains(query),
                Testing.code.contains(query),
                Testing.connections.contains(query),
                Testing.procedure.contains(query)
            )
        ).all()
    
    return render_template('search_results.html', 
                         projects=projects, 
                         testing_items=testing_items, 
                         query=query,
                         form=form)

@app.route('/search/projects')
@login_required
def search_projects():
    form = SearchForm()
    projects = []
    query = request.args.get('query', '')
    
    if query:
        projects = Project.query.filter(
            or_(
                Project.title.contains(query),
                Project.description.contains(query),
                Project.code.contains(query),
                Project.connections.contains(query),
                Project.procedure.contains(query)
            )
        ).all()
    
    return render_template('search_results.html', 
                         projects=projects, 
                         testing_items=[], 
                         query=query,
                         form=form,
                         search_type='projects')

@app.route('/search/testing')
@login_required
def search_testing():
    form = SearchForm()
    testing_items = []
    query = request.args.get('query', '')
    
    if query:
        testing_items = Testing.query.filter(
            or_(
                Testing.title.contains(query),
                Testing.description.contains(query),
                Testing.code.contains(query),
                Testing.connections.contains(query),
                Testing.procedure.contains(query)
            )
        ).all()
    
    return render_template('search_results.html', 
                         projects=[], 
                         testing_items=testing_items, 
                         query=query,
                         form=form,
                         search_type='testing')

@app.route('/profile')
@login_required
def profile():
    interests_list = current_user.interests.split(',') if current_user.interests else []
    recent_projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.desc()).limit(3).all()
    recent_testing = Testing.query.filter_by(user_id=current_user.id).order_by(Testing.created_at.desc()).limit(3).all()
    return render_template('profile.html', user=current_user, interests_list=interests_list,
                         recent_projects=recent_projects, recent_testing=recent_testing)

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    
    if form.validate_on_submit():
        # Check current password if trying to change password
        if form.new_password.data:
            if not form.current_password.data or not check_password_hash(current_user.password_hash, form.current_password.data):
                flash('Current password is required to change password.', 'danger')
                return render_template('edit_profile.html', form=form)
            current_user.password_hash = generate_password_hash(form.new_password.data)
        
        # Update profile photo if uploaded
        if form.profile_photo.data:
            if current_user.profile_photo:
                delete_file(current_user.profile_photo)
            current_user.profile_photo = save_uploaded_file(form.profile_photo.data, 'profiles')
        
        # Update other fields
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.interests = ','.join(form.interests.data)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    # Pre-populate form with current data
    form.username.data = current_user.username
    form.email.data = current_user.email
    if current_user.interests:
        form.interests.data = current_user.interests.split(',')
    
    return render_template('edit_profile.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Project routes
@app.route('/projects')
@login_required
def projects():
    all_projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=all_projects)

@app.route('/projects/<int:project_id>', methods=['GET', 'POST'])
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    comment_form = CommentForm()
    rating_form = RatingForm()
    
    # Handle comment submission
    if comment_form.validate_on_submit() and comment_form.submit.data:
        comment = ProjectComment(
            content=comment_form.content.data,
            user_id=current_user.id,
            project_id=project.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))
    
    # Handle rating submission
    if rating_form.validate_on_submit() and rating_form.submit.data:
        # Check if user already rated this project
        existing_rating = ProjectRating.query.filter_by(
            user_id=current_user.id, 
            project_id=project.id
        ).first()
        
        if existing_rating:
            existing_rating.rating = int(rating_form.rating.data)
        else:
            rating = ProjectRating(
                rating=int(rating_form.rating.data),
                user_id=current_user.id,
                project_id=project.id
            )
            db.session.add(rating)
        
        db.session.commit()
        flash('Your rating has been submitted!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))
    
    # Get average rating
    ratings = project.ratings
    avg_rating = sum(r.rating for r in ratings) / len(ratings) if ratings else 0
    user_rating = None
    if current_user.is_authenticated:
        user_rating = ProjectRating.query.filter_by(
            user_id=current_user.id, 
            project_id=project.id
        ).first()
        if user_rating:
            rating_form.rating.data = str(user_rating.rating)
    
    return render_template('project_detail.html', 
                         project=project, 
                         comment_form=comment_form,
                         rating_form=rating_form,
                         avg_rating=avg_rating,
                         user_rating=user_rating)

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

# Admin routes - Only allow owner access (user ID 1)
def admin_required(func):
    def decorated_function(*args, **kwargs):
        # Check if user is logged in and is the owner (user ID 1)
        if not current_user.is_authenticated or current_user.id != 1:
            abort(403)  # Forbidden - Only owner can access admin
            
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

@app.route('/admin/social-media', methods=['GET', 'POST'])
@admin_required
def admin_social_media():
    # Get or create social media settings
    social_media = SocialMediaLinks.query.first()
    if not social_media:
        social_media = SocialMediaLinks()
        db.session.add(social_media)
        db.session.commit()
    
    form = SocialMediaForm(obj=social_media)
    
    if form.validate_on_submit():
        social_media.youtube_url = form.youtube_url.data or ''
        social_media.instagram_url = form.instagram_url.data or ''
        social_media.github_url = form.github_url.data or ''
        social_media.linkedin_url = form.linkedin_url.data or ''
        social_media.twitter_url = form.twitter_url.data or ''
        
        db.session.commit()
        flash('Social media links updated successfully!', 'success')
        return redirect(url_for('admin_social_media'))
    
    return render_template('admin/social_media.html', form=form, social_media=social_media)

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
