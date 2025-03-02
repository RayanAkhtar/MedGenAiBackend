from flask import Blueprint, jsonify, request, flash, send_from_directory
import os
from werkzeug.utils import secure_filename
from __init__ import db
from services.admin.admin import (
    get_guesses_per_month,
    get_feedback_instances,
    get_total_real_images,
    get_total_ai_images,
    get_feedback_resolution_status,
    get_random_unresolved_feedback,
    upload_image_service,
    filter_users_by_tags,
    get_metadata_counts
)
from services.admin_user import create_user_game_session, get_game_by_game_id, get_user_data_by_username, get_users_with_filters


bp = Blueprint('admin', __name__)


@bp.route('/admin/getGuessesPerMonth', methods=['GET'])
def get_guesses_per_month_route():
    return jsonify(get_guesses_per_month())



@bp.route('/admin/getFeedbackInstances', methods=['GET'])
def get_feedback_instances_route():
    return jsonify(get_feedback_instances())

@bp.route('/admin/getTotalRealImages', methods=['GET'])
def get_total_real_images_route():
    return jsonify(get_total_real_images())

@bp.route('/admin/getTotalAIImages', methods=['GET'])
def get_total_ai_images_route():
    return jsonify(get_total_ai_images())

@bp.route('/admin/getFeedbackResolutionStatus', methods=['GET'])
def get_feedback_resolution_status_route():
    return jsonify(get_feedback_resolution_status())



@bp.route('/admin/getRandomUnresolvedFeedback/<image_id>', methods=['GET'])
def get_random_unresolved_feedback_route(image_id):
    return jsonify(get_random_unresolved_feedback(image_id))


@bp.route('/admin/uploadRealImage', methods=['POST'])
def upload_real_image_route():
    return upload_image_service(request, "real")

@bp.route('/admin/uploadAIImage', methods=['POST'])
def upload_ai_image_route():
    return upload_image_service(request, "ai")







@bp.route('/admin/getMetadataCounts', methods=['GET'])
def get_metadata_counts_route():
    try:
        counts = get_metadata_counts()  
        return jsonify(counts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/admin/filter-users', methods=['GET'])
def get_users_by_tags():
    """API to return users filtered by tags."""
    
    tag_names = request.args.getlist('tags')
    match_all = request.args.get('all', 'false').lower() == 'true'
    sort_by = request.args.get('sort_by', 'level').lower()
    desc = request.args.get('desc', 'true').lower() == 'true'
    if not tag_names:
        return jsonify({"error": "No tags provided"}), 400

    return jsonify(filter_users_by_tags(tag_names, match_all, sort_by, desc))

@bp.route('/admin/getUsers', methods=['GET'])
def get_users_data():
    level = request.args.get('level')
    min_games_won = request.args.get('min_games_won')
    max_games_won = request.args.get('max_games_won')
    min_score = request.args.get('min_score')
    max_score = request.args.get('max_score')
    sort_by = request.args.get('sort_by') 
    sort_order = request.args.get('sort_order', 'asc')

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    feedback_data = get_users_with_filters(
        level=level,
        min_games_won=min_games_won,
        max_games_won=max_games_won,
        max_score=max_score,
        min_score=min_score,
        sort_by=sort_by,
        sort_order=sort_order, 
        limit=limit, 
        offset=(page - 1) * limit
    )

    return jsonify(feedback_data)


@bp.route('/admin/getUsers/<username>', methods=['GET'])
def get_user_by_id(username):
    user_data = get_user_data_by_username(username)
    return jsonify(user_data)

@bp.route('/admin/getGame/<int:game_id>', methods=['GET'])
def get_game_by_id(game_id):
    return jsonify(get_game_by_game_id(game_id))

@bp.route('/admin/newGameSession/<int:game_id>/<int:user_id>')
def create_new_user_game_session(game_id, user_id):
    res, code = create_user_game_session(game_id, user_id)
    return jsonify({'status': code})