from flask import Blueprint, request, jsonify
from services.competition_service import CompetitionService
from middleware.auth import require_auth
from datetime import datetime
from __init__ import db
from models import Competition, CompetitionGame

competition_bp = Blueprint('competition', __name__)
competition_service = CompetitionService()

@competition_bp.route('/create', methods=['POST'])
def create_competition():
    """Create a new competition"""
    try:
        # Get competition data from request
        data = request.json
        
        # Create competition
        competition = competition_service.create_competition(data)
        
        return jsonify(competition), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error in create_competition: {str(e)}")
        return jsonify({"error": "Failed to create competition"}), 500

@competition_bp.route('/join/<int:competition_id>', methods=['GET'])
@require_auth
def join_competition(competition_id):
    """Join a competition using competition ID"""
    try:
        # Get user ID from auth middleware
        user_id = request.user_id
        
        # Find competition by ID
        competition = Competition.query.filter_by(competition_id=competition_id).first()
        if not competition:
            return jsonify({"error": "Competition not found"}), 404
            
        # Check if competition is active
        now = datetime.now()
        if now < competition.start_date or now > competition.end_date:
            return jsonify({"error": "Competition is not active"}), 400
            
        # Get the game associated with this competition
        competition_game = CompetitionGame.query.filter_by(competition_id=competition_id).first()
        if not competition_game:
            return jsonify({"error": "No game found for this competition"}), 404
            
        # Return game ID for the frontend to join
        return jsonify({
            "game_id": competition_game.game_id,
            "competition_name": competition.competition_name
        }), 200
        
    except Exception as e:
        print(f"Error in join_competition: {str(e)}")
        return jsonify({"error": "Failed to join competition"}), 500
