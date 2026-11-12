"""
============================================
  K&G Farms - Production WSGI Entry Point
  Used by Gunicorn, Waitress, and Render
============================================
"""
import os
from app import create_app

# Use 'production' environment by default, or read from FLASK_ENV
env = os.environ.get('FLASK_ENV', 'production')
app = create_app(env)

if __name__ == '__main__':
    # Optional fallback for local testing
    app.run()
