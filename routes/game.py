from flask import Blueprint, request, jsonify
from middleware.auth import require_auth
from models import Users, UserGuess, Images
from __init__ import db
from services.game_service import GameService

game_bp = Blueprint('game', __name__)
game_service = GameService()

@game_bp.route('/initialize-game', methods=['POST'])
@require_auth
def initialize_game():
    try:
        data = request.get_json()
        game_type = data.get('gameType')
        image_count = data.get('imageCount')
        user_id = request.user_id  # From @require_auth decorator


        print (f"Initializing game for user {user_id}")
        print(f"Game type: {game_type}")
        print(f"Image count: {image_count}")
        # Ensure user exists in database
        user = Users.query.filter_by(firebase_uid=user_id).first()
      
        if not user:
            return jsonify({
                'error': 'User not found',
                'status': 'error'
            }), 404
        
        print (f"User found: {user}")
        # Initialize game
        game_id, images = game_service.initialize_game(
            game_type=game_type,
            image_count=image_count,
            user_id=user.user_id  # Use database user_id
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
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
