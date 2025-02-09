from flask import Blueprint, jsonify, request, flash, send_from_directory
import os
from math import ceil
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
    get_feedback_with_filters,
    get_image_by_id,
    get_confusion_matrix,
    get_image_difficulty,
    get_leaderboard,
    get_ml_metrics,
    fetch_data_for_csv,
    get_metadata_counts
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


UPLOAD_FOLDER = 'images_get/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        
        # Create a subdirectory for real images if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        file.save(filepath)
        flash('Real image successfully uploaded')
        return jsonify({'message': 'Real image uploaded successfully', 'filepath': filepath}), 200

    flash('Invalid file type')
    return jsonify({'error': 'Invalid file type'}), 400


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
        
        # Create a subdirectory for ai images if it doesn't exist
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

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)  # 20 items per page by default
    resolved = True if resolved == 'true' else (False if resolved == 'false' else None)

    feedback_data, total_feedback_count = get_feedback_with_filters(
        image_type=image_type, resolved=resolved, sort_by=sort_by, 
        limit=limit, offset=(page - 1) * limit
    )
    
    total_pages = ceil(total_feedback_count / limit)
    response_data = {
        'feedback': feedback_data,
        'total': total_feedback_count,
        'total_pages': total_pages
    }

    return jsonify(response_data)


@bp.route('/admin/getImageById/<image_id>', methods=['GET'])
def get_image_by_id_route(image_id):
    image_data = get_image_by_id(image_id)
    if image_data:
        return jsonify(image_data), 200
    else:
        return jsonify({"error": "Image not found"}), 404


@bp.route('/admin/getConfusionMatrix', methods=['GET'])
def get_confusion_matrix_route():
    return jsonify(get_confusion_matrix())

@bp.route('/admin/getLeaderboard', methods=['GET'])
def get_leaderboard_route():
    return jsonify(get_leaderboard())

@bp.route('/admin/getImageDifficulty', methods=['GET'])
def get_image_difficulty_route():
    return jsonify(get_image_difficulty())

@bp.route('/admin/getMLMetrics', methods=['GET'])
def get_ml_metrics_route():
    try:
        ml_metrics = get_ml_metrics()
        return jsonify(ml_metrics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/downloadFeedbackData', methods=['GET'])
def download_feedback_data():
    try:
        if not os.path.exists('./downloads'):
            os.makedirs('./downloads')

        data = fetch_data_for_csv('feedback')
        csv_data = convert_to_csv(data)
        file_path = './downloads/feedback_data.csv'

        with open(file_path, 'w') as file:
            file.write(csv_data)

        print("wrote the file")

        return send_from_directory('downloads', 'feedback_data.csv', as_attachment=True)

    except Exception as e:
        print("exception", e)
        return str(e), 500


@bp.route('/admin/downloadImageData', methods=['GET'])
def download_image_data():
    try:
        data = fetch_data_for_csv('images')
        csv_data = convert_to_csv(data)
        file_path = os.path.join('downloads', 'image_data.csv')

        with open(file_path, 'w') as file:
            file.write(csv_data)

        return send_from_directory('downloads', 'image_data.csv', as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/admin/downloadLeaderboard', methods=['GET'])
def download_leaderboard_data():
    try:
        data = fetch_data_for_csv('users')
        csv_data = convert_to_csv(data)
        file_path = os.path.join('downloads', 'leaderboard_data.csv')

        with open(file_path, 'w') as file:
            file.write(csv_data)

        return send_from_directory('downloads', 'leaderboard_data.csv', as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/admin/downloadCompetitionData', methods=['GET'])
def download_competition_data():
    try:
        data = fetch_data_for_csv('competitions')
        csv_data = convert_to_csv(data)
        file_path = os.path.join('downloads', 'competition_data.csv')

        with open(file_path, 'w') as file:
            file.write(csv_data)

        return send_from_directory('downloads', 'competition_data.csv', as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/admin/getMetadataCounts', methods=['GET'])
def get_metadata_counts_route():
    try:
        counts = get_metadata_counts()  
        return jsonify(counts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/admin/feedbackCount', methods=['GET'])
def feedback_count():
    try:
        count = get_metadata_counts().get('feedback', 0)
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/admin/imageCount', methods=['GET'])
def image_count():
    try:
        count = get_metadata_counts().get('image', 0)
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/admin/leaderboardCount', methods=['GET'])
def leaderboard_count():
    try:
        count = get_metadata_counts().get('leaderboard', 0)
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/admin/competitionCount', methods=['GET'])
def competition_count():
    try:
        count = get_metadata_counts().get('competition', 0)
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def convert_to_csv(data):
    if not data:
        return "No data available"
    header = data[0].keys()
    rows = [','.join(str(value) for value in row.values()) for row in data]
    csv_data = ','.join(header) + '\n' + '\n'.join(rows)
    return csv_data