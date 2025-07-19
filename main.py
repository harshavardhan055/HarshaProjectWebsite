from app_init import app  # ✅ Import app from app_init
import routes  # ensure routes are registered
import jinja_filters  # ensure Jinja filters are loaded

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
