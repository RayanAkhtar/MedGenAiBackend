from flask import Blueprint, jsonify, request, flash
import os
from werkzeug.utils import secure_filename
from __init__ import db
from services.admin import (
    get_guesses_per_month,
    get_image_detection_accuracy,
    get_feedback_instances,
    get_total_real_images,
    get_total_ai_images,
    get_feedback_resolution_status,
    get_matching_feedback_for_image,
    get_random_unresolved_feedback,
    get_feedback_with_filters
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


# Set up the directory where images will be stored
UPLOAD_FOLDER = 'images_get/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Route to upload a real image
@bp.route('/admin/uploadRealImage', methods=['POST'])
def upload_real_image():
    if 'file' not in request.files:
        flash('No file part')
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, 'real', filename)
        
        # Create a subdirectory for 'real' images if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        file.save(filepath)
        flash('Real image successfully uploaded')
        return jsonify({'message': 'Real image uploaded successfully', 'filepath': filepath}), 200

    flash('Invalid file type')
    return jsonify({'error': 'Invalid file type'}), 400


# Route to upload an AI image
@bp.route('/admin/uploadAIImage', methods=['POST'])
def upload_ai_image():
    if 'file' not in request.files:
        flash('No file part')
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, 'ai', filename)
        
        # Create a subdirectory for 'ai' images if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        file.save(filepath)
        flash('AI image successfully uploaded')
        return jsonify({'message': 'AI image uploaded successfully', 'filepath': filepath}), 200

    flash('Invalid file type')
    return jsonify({'error': 'Invalid file type'}), 400


@bp.route('/admin/getFeedbacks', methods=['GET'])
def get_feedbacks_route():
    image_type = request.args.get('image_type')
    resolved = request.args.get('resolved')
    sort_by = request.args.get('sort_by')

    resolved = True if resolved == 'true' else (False if resolved == 'false' else None)

    feedback_data = get_feedback_with_filters(image_type=image_type, resolved=resolved, sort_by=sort_by)
    return jsonify(feedback_data)


