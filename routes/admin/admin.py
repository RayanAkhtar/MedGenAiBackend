from flask import Blueprint, jsonify, request, flash, send_from_directory
from sqlalchemy.exc import SQLAlchemyError
import os
import logging
from werkzeug.utils import secure_filename
from services.dual_game_service import create_dual_game
from __init__ import db
from services.admin.admin import (
    get_guesses_per_month,
    get_feedback_instances,
    get_total_real_images,
    get_total_ai_images,
    get_feedback_resolution_status,
    get_random_unresolved_feedback,
    upload_image_service,
    list_tags,
    paginated_filter_users_by_tags,
    count_users_by_tags,
    assign_tags_to_users,
    get_metadata_counts
)
from services.admin_user import (
    create_multiple_game_sessions, 
    create_user_game_session,
    get_assigned_games_by_username,
    get_game_by_game_code,
    get_user_data_by_username,
    get_users_with_filters
)
from sqlalchemy import func, extract
from models import UserGuess
from services.admin_user import create_user_game_session, get_game_by_game_code, get_user_data_by_username, get_users_with_filters

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

@bp.route('/admin/tags', methods=['GET'])
def tags():
	"""API to return list of all tags"""
	try:
	    admin_only = request.args.get('admin_only', 'false').lower() == 'true'
	    return jsonify(list_tags('4', admin_only))
	except Exception as e:
		logging.error(f"Server error: {str(e)}")
		return jsonify({"error": "An unexpected error occured"}), 500

@bp.route('/admin/filter-users', methods=['GET'])
def get_users_by_tags():
    """API to return users filtered by tags"""
    try:
        tag_names = request.args.getlist('tags')
        match_all = request.args.get('all', 'false').lower() == 'true'
        sort_by = request.args.get('sort_by', 'username').lower()
        desc = request.args.get('desc', 'true').lower() == 'true'
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        return jsonify(paginated_filter_users_by_tags(tag_names, match_all, sort_by, desc, limit, offset))
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@bp.route('/admin/count-users-by-tags', methods=['GET'])
def count_users_by_tags_api():
    """API to return number of users with specified tags"""

    try:
        tag_names = request.args.getlist('tags')
        match_all = request.args.get('all', 'false').lower() == 'true'
        return jsonify({"count": count_users_by_tags(tag_names, match_all)})
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@bp.route('/admin/assignTags', methods=['POST'])
def assign_tags_route():
    data = request.get_json()
    usernames = data.get('usernames', [])
    tags = data.get('tags', [])
    filter_tags = data.get('filterTags', [])
    admin_id = data.get('admin_id', '4')
    select_all = data.get('selectAll', False)
    match_all = data.get('all', False)
    
    if not usernames or not tags or not admin_id:
        return jsonify({"error": "usernames, tags, and admin_id are required fields."}), 400

    try:
        response = assign_tags_to_users(usernames, tags, admin_id, select_all, filter_tags, match_all)
        return response

    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Internal server error."}), 500

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


@bp.route('/admin/engagementHeatmap', methods=['GET'])
def get_engagement_heatmap():
    try:
        result = db.session.query(
            extract('year', UserGuess.date_of_guess).label('year'),
            extract('month', UserGuess.date_of_guess).label('month'),
            extract('week', UserGuess.date_of_guess).label('week'),
            extract('day', UserGuess.date_of_guess).label('day'),
            func.count().label('engagement')
        ).group_by('year', 'month', 'week', 'day').order_by('year', 'month', 'week', 'day').all()

        engagement_data = {}
        for row in result:
            year = int(row.year)
            month = int(row.month)
            week = int(row.week)
            day = int(row.day)
            engagement = row.engagement

            if year not in engagement_data:
                engagement_data[year] = {'data': []}

            engagement_data[year]['data'].append({
                'month': month,
                'week': week,
                'day': day,
                'engagement': engagement
            })

        formatted_data = []
        for year, data in engagement_data.items():
            formatted_data.append({
                'year': year,
                'data': data['data']
            })

        return jsonify(formatted_data)

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/getGame/<game_code>', methods=['GET'])
def get_game_by_code(game_code):
    return jsonify(get_game_by_game_code(game_code))

@bp.route('/admin/newGameSession', methods=['POST'])
def create_new_user_game_session():
    # Extract JSON from the request body
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400
    
    # Get fields from the JSON payload
    game_code = data.get('game_code')
    user_name = data.get('user_name')
    
    # Validate that both fields exist
    if game_code is None or user_name is None:
        return jsonify({'error': 'Missing "game_id" or "user_name"'}), 400
    
    # Call your function with the retrieved values
    res, code = create_user_game_session(game_code, user_name)
    
    # Return a JSON response

    if code == 200:
        return jsonify({'status': code}), 200
    else:
        return jsonify(res), code

@bp.route('/admin/newGameSession/multi', methods=['POST'])
def create_new_user_game_session_multi():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400
    game_code = data.get('game_code')
    usernames = data.get('usernames', [])
    select_all = data.get('selectAll', False)
    filter_tags = data.get('filterTags', [])
    match_all = data.get('all', False)
    
    if game_code is None:
        return jsonify({'error': 'Missing "game_id"'}), 400
    if not usernames and not select_all:
        return jsonify({'error': 'Missing "usernames" or "selectAll" must be true'}), 400
    res, code = create_multiple_game_sessions(game_code, usernames, select_all, filter_tags, match_all)

    if code == 200:
        return jsonify({'status': code}), 200
    else:
        return jsonify(res), code

@bp.route('/admin/getGames/<username>', methods=['GET'])
def get_games_by_user(username):
    user_data = get_assigned_games_by_username(username)
    return jsonify(user_data)

@bp.route('/admin/createDualGame', methods=['POST'])
def create_d_game():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400
    game_mode = data.get('game_mode')
    game_board = data.get('game_board')
    game_status = data.get('game_status')
    username = data.get('username')
    image_urls = data.get('image_urls')
    if game_mode is None or game_status is None or username is None or image_urls is None or game_board is None:
        return jsonify({'error': 'Missing required fields'}), 400
    res, code = create_dual_game(game_mode, game_status, username, image_urls)
    return jsonify(res), code
