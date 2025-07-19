from app_init import app # Just import the fully configured app instance

if __name__ == "__main__":
    # In a production environment like Render, Gunicorn handles serving,
    # so this block is primarily for local development.
    # Render will use the gunicorn command directly.
    PORT = os.environ.get("PORT", 5000) # Use environment variable for port
    print(f"✅ Server starting at http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
