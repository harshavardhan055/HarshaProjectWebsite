from app_init import app  # Corrected: Import app instance directly from app_init
import routes             # Ensure routes are registered
import jinja_filters      # Ensure Jinja filters are loaded

# Note: The database creation and default admin user setup logic
# that was previously in app.py should be handled separately.
# For deployment, this might be a pre-deploy hook or a manual step.
# For local development, you could create a dedicated setup script
# (e.g., `python setup_db.py`) to run it once.

if __name__ == "__main__":
    PORT = 5000 # Use port 5000 (default), or switch to another if needed (e.g., 8000 or 8080)

    print(f"✅ Server starting at http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
