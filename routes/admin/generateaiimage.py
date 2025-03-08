import os
from flask import Blueprint, request, jsonify, send_file
from services.admin.generateaiimage import generate_image
from werkzeug.utils import secure_filename
from __init__ import db
from models import Images
from datetime import datetime
import random

bp = Blueprint("adminGenerate", __name__)
REAL_IMAGES_PATH = "../MedGenAI-Images/Images/real_images"
UPLOAD_FOLDER = "../MedGenAI-Images/Images/generated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_IMAGES_PATH = "../MedGenAI-Images/Images"

@bp.route("/admin/generateImage", methods=["GET"])
def generate_image_route():
    age = request.args.get("age", "any")
    gender = request.args.get("sex", "any")
    disease = request.args.get("disease", "any")
    real_image_file_name = request.args.get("realImageFileName", None)
    image = generate_image(age, gender, disease, real_image_file_name)
    if image:
        return image
    else:
        return jsonify({"error": "No matching images found"}), 404


@bp.route("/admin/getRandomRealImagePath", methods=["GET"])
def get_random_real_image_path():
    """Fetch a random real image path and return it as JSON."""
    try:
        all_images = [f for f in os.listdir(REAL_IMAGES_PATH) if os.path.isfile(os.path.join(REAL_IMAGES_PATH, f))]
        
        if not all_images:
            return jsonify({"error": "No images found in real_images folder"}), 404
        
        selected_image = random.choice(all_images)
        image_path = f"real_images/{selected_image}"

        return jsonify({"imagePath": image_path, "fileName": selected_image})

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@bp.route("/admin/saveGeneratedImage", methods=["POST"])
def save_generated_image():
    gender = request.form.get("gender", "any")
    age = request.form.get("age", "any")
    disease = request.form.get("disease", "any")

    if "image" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(image.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        image.save(file_path)

        if gender == "any":
            gender = None
        if disease == "any":
            disease = None

        path_for_db = "/" + "/".join(file_path.split("/")[-2:])

        new_image = Images(
            image_path=path_for_db,
            image_type="ai",
            upload_time=datetime.utcnow(),
            gender=gender,
            age=age,
            disease=disease
        )
        db.session.add(new_image)
        db.session.commit()

        return jsonify(
            {
                "message": "Image saved successfully",
                "filePath": file_path,
                "image_id": new_image.image_id,
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/admin/<path:filename>")
def serve_image(filename):
    image_full_path = os.path.join(BASE_IMAGES_PATH, filename)
    if os.path.exists(image_full_path):
        return send_file(image_full_path, mimetype="image/jpeg")
    return jsonify({"error": "Image not found"}), 404
