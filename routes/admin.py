from flask import Blueprint, jsonify
from __init__ import db
from services.admin import (
    get_guesses_per_month,
    get_image_detection_accuracy,
    get_feedback_instances,
    get_total_real_images,
    get_total_ai_images,
    get_feedback_resolution_status,
    get_matching_feedback_for_image,
    get_random_unresolved_feedback
)

bp = Blueprint('admin', __name__)

@bp.route('/admin/getGuessesPerMonth', methods=['GET'])
def get_guesses_per_month_route():
    return jsonify(get_guesses_per_month())

@bp.route('/admin/getImageDetectionAccuracy', methods=['GET'])
def get_image_detection_accuracy_route():
    return jsonify(get_image_detection_accuracy())

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

@bp.route('/admin/getMatchingFeedbackForImage/<image_id>', methods=['GET'])
def get_matching_feedback_for_image_route(image_id):
    return jsonify(get_matching_feedback_for_image(image_id))

@bp.route('/admin/getRandomUnresolvedFeedback/<image_id>', methods=['GET'])
def get_random_unresolved_feedback_route(image_id):
    return jsonify(get_random_unresolved_feedback(image_id))
