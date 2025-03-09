import pytest
import json

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app import create_app
from models import db, Users, Game, Images, UserGameSession, Competition, GameImages
from datetime import datetime, timedelta
@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory SQLite for tests
    
    with app.app_context():
        db.create_all()
        # Create test data
        create_test_data()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def auth_header():
    """Generate a mock Firebase auth header for testing."""
    return {'Authorization': 'Bearer test-token'}

def create_test_data():
    """Create test data in the database."""
    try:
        # Create test user with unique ID
        import uuid
        user = Users(
            user_id=str(uuid.uuid4()),
            username=str(uuid.uuid4()),
            score=100,
            games_won=5,
            games_started=10
        )
        db.session.add(user)
        # Create test images
        images = []
        for i in range(1, 11):
            image = Images(
                image_path=f'test_images/{i}.jpg',
                image_type='real' if i <= 5 else 'ai',
                upload_time=datetime.now()
            )
            db.session.add(image)
            images.append(image)
        
        db.session.flush()  # Ensure images have IDs
        
        # Create test game first
        game_date = datetime.now()
        game_expiry = game_date + timedelta(days=7)
        
        game = Game(
            game_mode='classic',
            date_created=game_date,
            game_board='classic',
            game_status='active',
            expiry_date=game_expiry,
            created_by='test-user-id'
        )
        db.session.add(game)
        db.session.flush()  # Ensure game has ID
        
        # Create GameImages associations
        for image in images:
            game_image = GameImages(
                game_id=game.game_id,
                image_id=image.image_id
            )
            db.session.add(game_image)
        
        # Now create the competition using the game's ID and matching dates
        competition = Competition(
            competition_id=game.game_id,  # Set this to the game's ID
            competition_name='Test Competition',
            start_date=game_date,  # Match game's date_created
            end_date=game_expiry    # Match game's expiry_date
        )
        db.session.add(competition)
        
        # Create test session
        session = UserGameSession(
            game_id=game.game_id,
            user_id='test-user-id',
            start_time=datetime.now() - timedelta(hours=1),
            completion_time=datetime.now(),
            session_status='completed',
            correct_guesses=8,
            total_guesses=10,
            final_score=80
        )
        db.session.add(session)
        
        db.session.commit()
        print(f"Test data created successfully. Game ID: {game.game_id}, Competition ID: {competition.competition_id}")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating test data: {str(e)}")
        raise


# Mock the auth middleware for testing
def mock_auth_middleware():
    """Mock the auth middleware for tests."""
    from middleware import auth
    
    def mock_require_auth(f):
        def decorated(*args, **kwargs):
            from flask import request
            request.user_id = 'test-user-id'
            return f(*args, **kwargs)
        return decorated
    
    # Store original function if needed
    original_require_auth = auth.require_auth
    
    # Replace with mock
    auth.require_auth = mock_require_auth
    
    return original_require_auth


# Test 1: Verify the app can start
def test_app_exists(app):
    """Test that the app exists."""
    assert app is not None


# Test 2: Verify the test client can connect
def test_client_connection(client):
    """Test that the test client can connect to the app."""
    response = client.get('/')  # Just make any request
    # We don't care about the response, just that we got one without errors
    assert response is not None


# Test 3: Verify database connection
def test_database_connection(app):
    """Test that the database connection works."""
    with app.app_context():
        # Just retrieve something from the database
        user_count = Users.query.count()
        # We just verify we can query the database
        assert isinstance(user_count, int)