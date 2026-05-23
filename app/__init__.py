from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv

load_dotenv()

mongo = PyMongo()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/smart_job_portal')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'app/static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    mongo.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.candidate import candidate_bp
    from app.routes.employer import employer_bp
    from app.routes.admin import admin_bp
    from app.routes.resume import resume_bp
    from app.routes.interview import interview_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(employer_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(resume_bp, url_prefix='/resume')
    app.register_blueprint(interview_bp, url_prefix='/interview')
    app.register_blueprint(api_bp, url_prefix='/api')

    # User loader for Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    # Seed admin account on first run
    with app.app_context():
        _seed_admin()

    return app


def _seed_admin():
    """Ensure the admin account exists."""
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    admin = mongo.db.users.find_one({'email': 'admin@jobportal.in'})
    if not admin:
        mongo.db.users.insert_one({
            'name': 'Admin',
            'email': 'admin@jobportal.in',
            'password_hash': generate_password_hash('Admin@123'),
            'role': 'admin',
            'preferred_roles': [],
            'date_joined': datetime.utcnow(),
            'profile_summary': 'System Administrator',
            'avatar_color': '#7c3aed',
            'is_active': True,
            'is_approved': True,
        })