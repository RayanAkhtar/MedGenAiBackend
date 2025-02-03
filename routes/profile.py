from flask import jsonify, request
from __init__ import db
from models import Competition, CompetitionUser
from flask import Blueprint
from services.profile import get_profile_data, get_recent_game_history, get_user_performance, get_user_badges
bp = Blueprint('profile', __name__)

@bp.route('/api/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    return jsonify(get_profile_data(user_id))

@bp.route('/api/profile/<user_id>/recent-games', methods=['GET'])
def get_recent_games(user_id):
    return jsonify(get_recent_game_history(user_id))

@bp.route('/api/profile/<user_id>/performance', methods=['GET'])
def get_performance_data(user_id):
    return jsonify(get_user_performance(user_id))

@bp.route('/api/profile/<user_id>/badges', methods=['GET'])
def get_badges(user_id):
    return jsonify(get_user_badges(user_id))