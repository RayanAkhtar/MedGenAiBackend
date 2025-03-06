from flask import Blueprint, jsonify, request
from services.admin.managetags import get_tags, add_tag, update_tag, delete_tag, add_tag_for_user, delete_tag_for_user, get_tags_for_user

bp = Blueprint('adminTags', __name__)

@bp.route('/admin/getTags', methods=['GET'])
def get_tags_route():
    try:
        tags = get_tags()
        return jsonify(tags), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/admin/addTag', methods=['POST'])
def add_tag_route():
    try:
        data = request.get_json()
        name = data.get('name')
        admin_id = data.get('admin_id')

        new_tag = add_tag(name, admin_id)
        
        return jsonify(new_tag), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/updateTag/<tag_id>', methods=['POST'])
def update_tag_route(tag_id):
    try:
        data = request.get_json()
        updated_tag = update_tag(tag_id, data.get('name'))
        return jsonify(updated_tag), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/admin/deleteTag/<tag_id>', methods=['DELETE'])
def delete_tag_route(tag_id):
    try:
        delete_tag(tag_id)
        return jsonify({'message': 'Tag deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/admin/addTagForUser', methods=['POST'])
def add_tag_for_user_route():
    try:
        data = request.get_json()
        user_id = data.get('userId')
        tag_id = data.get('tagId')

        if not user_id or not tag_id:
            return jsonify({'error': 'Missing userId or tagId'}), 400

        add_tag_for_user(user_id, tag_id)
        return jsonify({'message': 'Tag added successfully for user'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/admin/deleteTagForUser', methods=['DELETE'])
def delete_tag_for_user_route():
    try:
        data = request.get_json()
        user_id = data.get('userId')
        tag_id = data.get('tagId')

        if not user_id or not tag_id:
            return jsonify({'error': 'Missing userId or tagId'}), 400

        delete_tag_for_user(user_id, tag_id)
        return jsonify({'message': 'Tag deleted successfully for user'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/admin/getTagsForUser/<username>', methods=['GET'])
def get_tags_for_user_route(username):
    try:
        tags = get_tags_for_user(username)
        return jsonify(tags), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
