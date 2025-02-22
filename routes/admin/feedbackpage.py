from flask import jsonify, request, Blueprint
from services.admin.feedbackpage import (
    get_feedback_count,
    get_feedback_with_filters,
    resolve_all_feedback_by_image
)

from routes.admin.admin import bp


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



