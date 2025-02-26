from flask import Blueprint, request, jsonify
from services.admin.generateaiimage import generate_image

bp = Blueprint("adminGenerate", __name__)

@bp.route("/admin/generateImage", methods=["GET"])
def generate_image_route():
    age = request.args.get("age", "any")
    gender = request.args.get("sex", "any")
    disease = request.args.get("disease", "any")

    image_url = generate_image(age, gender, disease)
    if image_url:
        return jsonify({"imagePath": image_url})
    else:
        return jsonify({"error": "No matching images found"}), 404
