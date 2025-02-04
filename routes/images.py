from flask import jsonify, send_from_directory
from services.images import get_image_list
from flask import Blueprint
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
