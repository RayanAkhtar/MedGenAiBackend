from flask import Blueprint, jsonify

from services.admin.metrics import (
    get_image_detection_accuracy, 
    get_confusion_matrix, 
    get_ml_metrics, 
    get_leaderboard, 
    get_image_difficulty
)


bp = Blueprint('admin', __name__)


@bp.route('/admin/getImageDetectionAccuracy', methods=['GET'])
def get_image_detection_accuracy_route():
    return jsonify(get_image_detection_accuracy())

@bp.route('/admin/getConfusionMatrix', methods=['GET'])
def get_confusion_matrix_route():
    return jsonify(get_confusion_matrix())


@bp.route('/admin/getMLMetrics', methods=['GET'])
def get_ml_metrics_route():
    try:
        ml_metrics = get_ml_metrics()
        return jsonify(ml_metrics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@bp.route('/admin/getLeaderboard', methods=['GET'])
def get_leaderboard_route():
    return jsonify(get_leaderboard())


@bp.route('/admin/getImageDifficulty', methods=['GET'])
def get_image_difficulty_route():
    return jsonify(get_image_difficulty())