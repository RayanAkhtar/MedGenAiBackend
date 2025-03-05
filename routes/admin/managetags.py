from flask import Blueprint, jsonify, request
from services.admin.tags import get_tags, add_tag, update_tag, delete_tag

bp = Blueprint('adminTags', __name__)

# Get all tags
@bp.route('/admin/getTags', methods=['GET'])
def get_tags_route():
    try:
        tags = get_tags()
        return jsonify(tags), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add a new tag
@bp.route('/admin/addTag', methods=['POST'])
def add_tag_route():
    try:
        data = request.get_json()
        new_tag = add_tag(data.get('name'), data.get('isPrivate'))
        return jsonify(new_tag), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update a tag
@bp.route('/admin/updateTag/<tag_id>', methods=['POST'])
def update_tag_route(tag_id):
    try:
        data = request.get_json()
        updated_tag = update_tag(tag_id, data.get('name'))
        return jsonify(updated_tag), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete a tag
@bp.route('/admin/deleteTag/<tag_id>', methods=['DELETE'])
def delete_tag_route(tag_id):
    try:
        delete_tag(tag_id)
        return jsonify({'message': 'Tag deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
