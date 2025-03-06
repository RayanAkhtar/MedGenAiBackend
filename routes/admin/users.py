
from flask import Blueprint, jsonify

from services.admin.users import (
    get_accuracy_for_user,
    get_total_images_attempted_for_user
)

bp = Blueprint('adminusers', __name__)




@bp.route('/admin/getAccuracyForUser/<username>', methods=['GET'])
def get_accuracy_for_user_route(username):
    try:
        accuracy = get_accuracy_for_user(username)
        return jsonify({'accuracy': accuracy}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/admin/getTotalImagesAttemptedForUser/<username>', methods=['GET'])
def get_total_images_attempted_for_user_route(username):
    try:
        total_images_attempted = get_total_images_attempted_for_user(username)
        return jsonify({'totalImagesAttempted': total_images_attempted}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    