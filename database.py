from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import sys

db = SQLAlchemy()
login_manager = LoginManager()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access the K&G Farms dashboard.'
login_manager.login_message_category = 'warning'


def init_db(app):
    """Initialize database with the Flask app"""
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        try:
            import models
            from models import User

            db.create_all()
            print("[K&G Farms] ✅ Database tables created successfully!", flush=True)

            # Create default admin if no admin exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                from werkzeug.security import generate_password_hash
                default_admin = User(
                    username='admin',
                    email='kgfarms.business@gmail.com',
                    password_hash=generate_password_hash('admin123'),
                    full_name='Farm Administrator',
                    role='admin',
                    is_active=True
                )
                db.session.add(default_admin)
                db.session.commit()
                print("[K&G Farms] ✅ Default admin created (admin / admin123)", flush=True)
        except Exception as e:
            print(f"[K&G Farms ERROR in init_db]: {str(e)}", file=sys.stderr, flush=True)
            # Re-raise so Render logs show the exact database trace if connection fails
            raise e
