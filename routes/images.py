from flask import jsonify, send_from_directory, Blueprint, request
from services.images import get_image_list, get_images_rand
import os

bp = Blueprint('images', __name__)

@bp.route('/api/images', methods=['GET'])
def list_images():
    """
    Returns a list of all image URLs.
    """
    print("Fetching image list...")
    return jsonify(get_image_list())

@bp.route('/api/images/view/<path:image_path>', methods=['GET'])
def view_image(image_path):
    """
    Serves a specific image file.
    """
    # Dynamically locate the Images folder
    BASE_IMAGES_PATH = os.path.abspath(os.path.join(os.getcwd(), "../MedGenAI-Images/Images"))

    # Debugging output
    print("Current Directory:", os.getcwd())
    print("Base Images Path:", BASE_IMAGES_PATH)

    # Join the base path with the relative image path
    full_image_path = os.path.join(BASE_IMAGES_PATH, image_path)
    print("Full Image path:", full_image_path)

    # Serve the file if it exists
    if os.path.exists(full_image_path):
        return send_from_directory(BASE_IMAGES_PATH, image_path)
    return jsonify({"error": "Image not found"}), 404

@bp.route('/api/images/mixed', methods=['GET'])
def get_mixed_images():
    """
    API to return an equal mix of real and fake images.
    Usage: /api/images/mixed?count=10
    """
    count = request.args.get('count', type=int)
    if count is None:
        return jsonify({"error": "Missing required parameter: count"}), 400  # Bad Request
    half_count = max(count // 2, 1)

    real_images = get_images_rand(half_count, 'real')
    cf_images = get_images_rand(half_count, 'ai')
    return jsonify({"real": real_images, "cf": cf_images})
