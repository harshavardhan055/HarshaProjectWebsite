from app_init import app  # ✅ Import app from app_init
import routes  # noqa: F401  — ensure routes are registered
import jinja_filters  # noqa: F401  — ensure Jinja filters are loaded

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

