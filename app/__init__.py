from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# دي أهم سطرين: لازم يكونوا بره الـ create_app عشان يحلوا مشكلة الـ Circular Import
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key-123')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instructors.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from .models import User
        from .seed_data import seed_database
        
        db.create_all()
        seed_database()

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # استدعاء البلوبرنتس
        from .routes.main import main_bp
        from .routes.instructors import instructors_bp
        from .routes.dashboard import dashboard_bp
        from .routes.lookups import lookups_bp
        from .routes.auth import auth_bp
        from .routes.plans import plans_bp
        from .routes.users import users_bp
        from .routes.logs import logs_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(instructors_bp, url_prefix='/instructors')
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
        app.register_blueprint(lookups_bp, url_prefix='/api/lookups')
        app.register_blueprint(auth_bp)
        app.register_blueprint(plans_bp, url_prefix='/plans')
        app.register_blueprint(users_bp, url_prefix='/users')
        app.register_blueprint(logs_bp, url_prefix='/logs')

    return app