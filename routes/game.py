from flask import Blueprint, request, jsonify
from middleware.auth import require_auth
from models import Users, UserGuess, Images
from __init__ import db
from services.game_service import GameService
import random

game_bp = Blueprint('game', __name__)
game_service = GameService()

@game_bp.route('/initialize-classic-game', methods=['POST'])
@require_auth
def initialize_classic_game():
    """
    Initialize a classic game where users guess between real and AI images
    """
    try:
        data = request.get_json()
        image_count = data.get('imageCount', 10)  # Default to 10 images if not specified
        user_id = request.user_id  # From @require_auth decorator

        print(f"Initializing classic game for user {user_id}")
        print(f"Image count: {image_count}")
        
        # Ensure user exists in database
        user = Users.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({
                'error': 'User not found',
                'status': 'error'
            }), 404
        
        print(f"User found: {user}")
        
        # Initialize classic game - will get a mix of real and AI images
        game_id, images = game_service.initialize_classic_game(
            image_count=image_count,
            user_id=user.user_id
        )

        # Update user's games_started count
        user.games_started += 1
        db.session.commit()

        return jsonify({
            'gameId': game_id,
            'images': images,
            'status': 'success'
        })

    except ValueError as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 400
    except Exception as e:
        print(f"Error in initialize_classic_game: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
