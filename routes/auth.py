from flask import Blueprint, request, jsonify
from models import Users
from __init__ import db
from middleware.auth import require_auth

auth_signup_bp = Blueprint('auth_signup', __name__)
# sharif branch
@auth_signup_bp.route('/auth/register', methods=['POST'])
@require_auth
def register_user():
    try:
        print("Starting register_user function")
        # Get user data from request
        data = request.get_json()
        print(f"Request data: {data}")
        
        firebase_uid = request.user_id  # This is the Firebase UID from the token
        print(f"Firebase UID: {firebase_uid}")
        
        username = data.get('username')
        print(f"Username: {username}")

        # Check if user already exists
        print("Checking if user exists...")
        existing_user = Users.query.filter_by(user_id=firebase_uid).first()
        print(f"Existing user query result: {existing_user}")
        
        if existing_user:
            print("User already exists, returning 409")
            return jsonify({
                'error': 'User already exists',
                'userId': existing_user.user_id
            }), 409

        # Create new user using Firebase UID as the user_id
        print("Creating new user...")
        new_user = Users(
            user_id=firebase_uid,     # Using Firebase UID directly as user_id
            username=username,
            level=1,
            exp=0,
            games_started=0,
            games_won=0,
            score=0
        )
        print(f"New user object created: {new_user.__dict__}")

        print("Adding user to database session...")
        db.session.add(new_user)
        print("Committing to database...")
        db.session.commit()
        print("Database commit successful")

        return jsonify({
            'message': 'User registered successfully',
            'userId': new_user.user_id
        }), 201

    except Exception as e:
        print(f"Error in register_user: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_signup_bp.route('/auth/user', methods=['GET'])
@require_auth
def get_user():
    try:
        print("Starting get_user function")
        firebase_uid = request.user_id
        print(f"Firebase UID: {firebase_uid}")
        
        print("Querying for user...")
        user = Users.query.filter_by(firebase_uid=firebase_uid).first()
        print(f"User query result: {user}")
        
        if not user:
            print("User not found, returning 404")
            return jsonify({
                'exists': False
            }), 404
            
        print("User found, returning user data")
        return jsonify({
            'exists': True,
            'user': {
                'userId': user.user_id,
                'username': user.username,
                'level': user.level,
                'exp': user.exp,
                'gamesStarted': user.games_started,
                'gamesWon': user.games_won,
                'score': user.score
            }
        }), 200

    except Exception as e:
        print(f"Error in get_user: {str(e)}")
        return jsonify({'error': str(e)}), 500

