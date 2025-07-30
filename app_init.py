from flask import Flask
from routes import main as main_blueprint
from admin import admin as admin_blueprint  # if admin routes exist

app = Flask(__name__)
app.secret_key = 'a3f1e790b8d64c85a3b9e2a49f31e938bb8c1d374e8c9c3f9e5e8f6b8dfc5a6d'


# Register Blueprints
app.register_blueprint(main_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")  # Optional
