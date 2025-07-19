import os
from application import app, db  # ✅ fixed circular import
from models import User
from werkzeug.security import generate_password_hash

db_path = os.path.join(app.root_path, "harsha_projects.db")

# Step 1: Delete existing DB
if os.path.exists(db_path):
    os.remove(db_path)
    print("✅ Old database removed.")

# Step 2: Recreate DB
with app.app_context():
    db.create_all()
    print("✅ Database created.")

    # Step 3: Add default admin user
    if not User.query.filter_by(username="admin").first():
        admin_user = User(
            username="admin",
            email="mastertechnical193@gmail.com",
            password_hash=generate_password_hash("admin"),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin user added (username: admin, password: admin)")



