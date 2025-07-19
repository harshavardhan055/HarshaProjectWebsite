from app_init import app  # ✅ Import app instance from app_init
import routes             # ✅ Ensure routes are registered (this is handled by app_init now)
import jinja_filters      # ✅ Ensure Jinja filters are loaded

if __name__ == "__main__":
    # Use port 5000 (default), or switch to another if needed (e.g., 8000 or 8080)
    PORT = 5000

    print(f"✅ Server starting at http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
