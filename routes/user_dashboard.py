from flask import Blueprint, request, jsonify
from services.user_dashboard_service import UserDashboardService
from middleware.auth import require_auth

user_dashboard = Blueprint('user_dashboard', __name__)
dashboard_service = UserDashboardService()

@user_dashboard.route('/stats', methods=['GET'])
@require_auth
def get_user_stats():
    """Get user statistics for the dashboard"""
    try:
        user_id = request.user_id
        stats = dashboard_service.get_user_stats(user_id)
        return jsonify(stats)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(f"Error in get_user_stats: {str(e)}")
        return jsonify({"error": "Failed to retrieve user stats"}), 500


@user_dashboard.route('/recent-activity', methods=['GET'])
@require_auth
def get_recent_activity():
    """Get user's recent game activity"""
    try:
        user_id = request.user_id
        activity = dashboard_service.get_recent_activity(user_id)
        return jsonify(activity)
        
    except Exception as e:
        print(f"Error in get_recent_activity: {str(e)}")
        return jsonify({"error": "Failed to retrieve recent activity"}), 500


@user_dashboard.route('/leaderboard', methods=['GET'])
@require_auth
def get_leaderboard():
    """Get global leaderboard data"""
    try:
        leaderboard = dashboard_service.get_leaderboard()
        return jsonify(leaderboard)
        
    except Exception as e:
        print(f"Error in get_leaderboard: {str(e)}")
        return jsonify({"error": "Failed to retrieve leaderboard data"}), 500
    