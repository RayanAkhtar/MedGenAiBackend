import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialize the database object
db = SQLAlchemy()

def create_app():
    # Initialize Flask app
    app = Flask(__name__)

    # Enable CORS for all domains (you can restrict it later as needed)
    CORS(app)

    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///medgen.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # Initialize the database with the app
    db.init_app(app)

    # Import and register blueprints (this allows you to modularize your routes)
    from . import app  # import the routes from main.py
    app.register_blueprint(app.bp)

    return app
