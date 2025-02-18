from flask import Blueprint, jsonify, request, flash, send_from_directory
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
    get_feedback_with_filters,
    get_image_by_id,
    get_confusion_matrix,
    get_image_confusion_matrix,
    get_image_difficulty,
    get_leaderboard,
    get_ml_metrics,
    fetch_data_for_csv,
    get_metadata_counts,
    get_feedback_count,
    upload_image_service,
    resolve_all_feedback_by_image,
    filter_users_by_tags
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



@bp.route('/admin/uploadRealImage', methods=['POST'])
def upload_real_image_route():
    return upload_image_service(request, "real")

@bp.route('/admin/uploadAIImage', methods=['POST'])
def upload_ai_image_route():
    return upload_image_service(request, "ai")


@bp.route('/admin/getFeedbacks', methods=['GET'])
def get_feedbacks_route():
    image_type = request.args.get('image_type')
    resolved = request.args.get('resolved')
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order', 'asc')
    resolved = True if resolved == 'true' else (False if resolved == 'false' else None)

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    feedback_data = get_feedback_with_filters(
        image_type=image_type, 
        resolved=resolved, 
        sort_by=sort_by,
        sort_order=sort_order, 
        limit=limit, 
        offset=(page - 1) * limit
    )

    return jsonify(feedback_data)

@bp.route('/admin/getFeedbackCount', methods=['GET'])
def get_feedback_count_route():
    image_type = request.args.get('image_type')
    resolved = request.args.get('resolved')

    resolved = True if resolved == 'true' else (False if resolved == 'false' else None)
    total_count = get_feedback_count(image_type=image_type, resolved=resolved)

    return jsonify({'total_count': total_count})


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



@bp.route('/admin/getImageMlMetrics/<image_id>', methods=['GET'])
def get_image_ml_metrics(image_id):
    try:
        confusion_matrix = get_image_confusion_matrix(image_id)

        TP = confusion_matrix.get('truepositive', 0)
        FP = confusion_matrix.get('falsepositive', 0)
        FN = confusion_matrix.get('falsenegative', 0)
        TN = confusion_matrix.get('truenegative', 0)
        print("confusion matrix is", confusion_matrix)
        accuracy = (TP + TN) / (TP + FP + FN + TN) if (TP + FP + FN + TN) > 0 else 0
        
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        precision_rev = TN / (TN + FN) if (TN + FN) > 0 else 0
        precision = max(precision, precision_rev)
        
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        recall_rec = TN / (TN + FP) if (TN + FP) > 0 else 0
        recall = max(recall, recall_rec)

        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        metrics = {
            'confusionMatrix': confusion_matrix,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1Score': f1_score,
        }

        return jsonify(metrics), 200

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


@bp.route('/admin/resolveAllFeedbackByImage/<image_id>', methods=['POST'])
def resolve_all_feedback_by_image_route(image_id):
    try:
        if not image_id:
            return jsonify({"error": "imageId is required"}), 400

        # Call the service function to resolve feedback for the image
        result = resolve_all_feedback_by_image(image_id)

        if result.get('error'):
            return jsonify(result), 500  # Return error if there is an issue
        
        return jsonify(result)  # Return success message
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/admin/filter-users', methods=['GET'])
def get_users_by_tags():
    """API to return users filtered by tags."""
    
    tag_names = request.args.getlist('tags')
    match_all = request.args.get('all', 'false').lower() == 'true'
    if not tag_names:
        return jsonify({"error": "No tags provided"}), 400

    return jsonify(filter_users_by_tags(tag_names, match_all))

