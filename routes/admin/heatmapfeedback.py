from flask import Blueprint, jsonify
import os
from __init__ import db

from services.admin.heatmapfeedback import (
    get_image_by_id,
    get_image_confusion_matrix,
    get_matching_feedback_for_image
)



bp = Blueprint('admin', __name__)

@bp.route('/admin/getImageById/<image_id>', methods=['GET'])
def get_image_by_id_route(image_id):
    image_data = get_image_by_id(image_id)
    if image_data:
        return jsonify(image_data), 200
    else:
        return jsonify({"error": "Image not found"}), 404
    

@bp.route('/admin/getMatchingFeedbackForImage/<image_id>', methods=['GET'])
def get_matching_feedback_for_image_route(image_id):
    return jsonify(get_matching_feedback_for_image(image_id))


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

