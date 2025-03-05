from flask import Blueprint, request, jsonify
from services.profile import get_profile_data, get_recent_game_history, get_user_performance
from middleware.auth import require_auth

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/data', methods=['GET'])
@require_auth
def profile_data():
    """Get user profile data"""
    try:
        user_id = request.user_id
        profile_data = get_profile_data(user_id)
        return jsonify(profile_data)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(f"Error in profile_data: {str(e)}")
        return jsonify({"error": "Failed to retrieve profile data"}), 500

@profile_bp.route('/game-history', methods=['GET'])
@require_auth
def game_history():
    """Get user's game history"""
    try:
        user_id = request.user_id
        history = get_recent_game_history(user_id)
        return jsonify(history)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(f"Error in game_history: {str(e)}")
        return jsonify({"error": "Failed to retrieve game history"}), 500

@profile_bp.route('/performance', methods=['GET'])
@require_auth
def performance():
    """Get user's performance data"""
    try:
        user_id = request.user_id
        performance_data = get_user_performance(user_id)
        return jsonify(performance_data)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(f"Error in performance: {str(e)}")
        return jsonify({"error": "Failed to retrieve performance data"}), 500

