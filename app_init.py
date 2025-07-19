# app_init.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///harsha_projects.db'
app.config['SECRET_KEY'] = 'your-secret-key'

db = SQLAlchemy(app)
