import os
from flask import Blueprint, request, jsonify
from services.admin.generateaiimage import generate_image
from werkzeug.utils import secure_filename

bp = Blueprint("adminGenerate", __name__)

@bp.route("/admin/generateImage", methods=["GET"])
def generate_image_route():
    age = request.args.get("age", "any")
    gender = request.args.get("sex", "any")
    disease = request.args.get("disease", "any")

    image = generate_image(age, gender, disease)
    if image:
        return image
    else:
        return jsonify({"error": "No matching images found"}), 404



UPLOAD_FOLDER = "../MedGenAI-Images/Images/generated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route("/admin/saveImage", methods=["POST"])
def save_image_route():
    if "image" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(image.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        image.save(file_path)
        return jsonify({"message": "Image saved successfully", "filePath": file_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500