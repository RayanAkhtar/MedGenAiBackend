from flask import Blueprint, request, jsonify
from models import Users
from __init__ import db
from middleware.auth import require_auth

auth_signup_bp = Blueprint('auth_signup', __name__)

@auth_signup_bp.route('/auth/register', methods=['POST'])
@require_auth  # This ensures we have a valid Firebase token
def register_user():
    try:
        # Get user data from request
        data = request.get_json()
        firebase_uid = request.user_id  # This comes from the @require_auth decorator
        username = data.get('username')

        # Check if user already exists
        existing_user = Users.query.filter_by(firebase_uid=firebase_uid).first()
        if existing_user:
            return jsonify({
                'error': 'User already exists',
                'userId': existing_user.user_id
            }), 409

        # Create new user
        new_user = Users(
            firebase_uid=firebase_uid,
            username=username,
            level=1,
            exp=0,
            games_started=0,
            games_won=0,
            score=0
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'message': 'User registered successfully',
            'userId': new_user.user_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_signup_bp.route('/auth/user', methods=['GET'])
@require_auth
def get_user():
    try:
        firebase_uid = request.user_id
        user = Users.query.filter_by(firebase_uid=firebase_uid).first()
        
        if not user:
            return jsonify({
                'exists': False
            }), 404
            
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
        return jsonify({'error': str(e)}), 500 