from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, EmailField, TextAreaField, FileField, SubmitField, BooleanField, SelectMultipleField, HiddenField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    interests = SelectMultipleField('Interests', choices=[
        ('electronics', 'Electronics'),
        ('programming', 'Programming'),
        ('iot', 'Internet of Things'),
        ('robotics', 'Robotics'),
        ('web_development', 'Web Development'),
        ('mobile_development', 'Mobile Development'),
        ('ai_ml', 'AI/Machine Learning'),
        ('embedded_systems', 'Embedded Systems'),
        ('hardware_design', 'Hardware Design'),
        ('software_testing', 'Software Testing')
    ])
    submit = SubmitField('Send Verification Code')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EmailVerificationForm(FlaskForm):
    email = HiddenField()
    otp = StringField('Verification Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify Email')

class SearchForm(FlaskForm):
    query = StringField('Search projects and testing...', validators=[DataRequired()])
    submit = SubmitField('Search')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    profile_photo = FileField('Profile Photo', validators=[FileAllowed(['jpg', 'png', 'gif'], 'Images only!')])
    interests = SelectMultipleField('Interests', choices=[
        ('electronics', 'Electronics'),
        ('programming', 'Programming'),
        ('iot', 'Internet of Things'),
        ('robotics', 'Robotics'),
        ('web_development', 'Web Development'),
        ('mobile_development', 'Mobile Development'),
        ('ai_ml', 'AI/Machine Learning'),
        ('embedded_systems', 'Embedded Systems'),
        ('hardware_design', 'Hardware Design'),
        ('software_testing', 'Software Testing')
    ])
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password', validators=[Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])
    submit = SubmitField('Update Profile')

class CommentForm(FlaskForm):
    content = TextAreaField('Your Comment', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Post Comment')

class RatingForm(FlaskForm):
    rating = SelectField('Rate this Project', choices=[
        ('1', '1 Star - Poor'),
        ('2', '2 Stars - Fair'),
        ('3', '3 Stars - Good'),
        ('4', '4 Stars - Very Good'),
        ('5', '5 Stars - Excellent')
    ], validators=[DataRequired()])
    submit = SubmitField('Submit Rating')

class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Project Image')
    code = TextAreaField('Code')
    video = FileField('Video')
    circuit_diagram = FileField('Circuit Diagram')
    connections = TextAreaField('Connections')
    procedure = TextAreaField('Procedure')
    submit = SubmitField('Save Project')

class TestingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Testing Image')
    code = TextAreaField('Code')
    video = FileField('Video')
    circuit_diagram = FileField('Circuit Diagram')
    connections = TextAreaField('Connections')
    procedure = TextAreaField('Procedure')
    submit = SubmitField('Save Testing Item')

class SocialMediaForm(FlaskForm):
    youtube_url = StringField('YouTube Channel URL', validators=[Length(max=256)])
    instagram_url = StringField('Instagram Profile URL', validators=[Length(max=256)])
    github_url = StringField('GitHub Profile URL', validators=[Length(max=256)])
    linkedin_url = StringField('LinkedIn Profile URL', validators=[Length(max=256)])
    twitter_url = StringField('Twitter Profile URL', validators=[Length(max=256)])
    submit = SubmitField('Update Social Media Links')
