from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from flask_migrate import Migrate
import os

load_dotenv()

db = SQLAlchemy()
cors = CORS()
migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__)


    # Configure the app
    uri = os.environ.get('DATABASE_URL', 'postgresql://medgen_user:blackberry@localhost/medgen')
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    if test_config is not None:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    with app.app_context():
        # Register blueprints
        from routes import bp
        from routes.profile import profile_bp
        from routes.images import bp as image_bp
        from routes.competitions import bp as comp_bp

        from routes.admin.admin import bp as admin_bp
        from routes.admin.download import bp as admin_download_bp
        from routes.admin.feedbackpage import bp as admin_feedback_bp
        from routes.admin.metrics import bp as admin_metrics_bp
        from routes.admin.heatmapfeedback import bp as admin_heatmap_bp
        from routes.admin.generateaiimage import bp as generate_image_bp
        from routes.scripts import bp as scripts_bp
        from routes.admin.managetags import bp as manage_tags_bp
        from routes.admin.users import bp as admin_users_bp

        from routes.game import  game_bp
        from middleware.auth import auth_bp
        from routes.auth import auth_signup_bp
        from routes.user_dashboard import user_dashboard
        app.register_blueprint(bp)
        app.register_blueprint(profile_bp, url_prefix='/profile')
        app.register_blueprint(comp_bp)


        app.register_blueprint(admin_bp)
        app.register_blueprint(admin_download_bp)
        app.register_blueprint(admin_feedback_bp)
        app.register_blueprint(admin_metrics_bp)
        app.register_blueprint(admin_heatmap_bp)
        app.register_blueprint(generate_image_bp)
        app.register_blueprint(manage_tags_bp)
        app.register_blueprint(admin_users_bp)

        app.register_blueprint(image_bp)
        app.register_blueprint(game_bp, url_prefix='/game')
        app.register_blueprint(auth_bp)
        app.register_blueprint(auth_signup_bp)
        app.register_blueprint(user_dashboard, url_prefix='/user_dashboard')
        app.register_blueprint(scripts_bp)

    print(app.url_map)
    return app 
