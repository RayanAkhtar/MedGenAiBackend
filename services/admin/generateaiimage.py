import os
from flask import request, jsonify, send_file, url_for
from models import Images
from sqlalchemy.sql.expression import func

BASE_IMAGES_PATH = os.path.abspath(os.path.join(os.getcwd(), "../MedGenAI-Images/Images"))

def map_age_range(age_range):
    age_mapping = {
        "18-25": (18, 25),
        "26-35": (26, 35),
        "36-45": (36, 45),
        "46-60": (46, 60),
        "60+": (60, 120)
    }
    return age_mapping.get(age_range, None)

def generate_image(age: str = "", gender: str = "", disease: str = ""):
    query = Images.query

    if age and age != "any":
        age_range = map_age_range(age)
        if age_range:
            query = query.filter(Images.age.between(*age_range))
    if gender and gender != "any":
        query = query.filter(Images.gender == gender)
    if disease and disease != "any":
        query = query.filter(Images.disease == disease)

    image = query.order_by(func.random()).first()

    if image:
        image_path = image.image_path
        image_url = url_for('serve_image', filename=image_path, _external=True)  # Generate an absolute URL

        return jsonify({
            "imagePath": image_url  # Send the full image URL instead of the hex data
        })

    return jsonify({"error": "No matching image found"}), 404


@bp.route('/admin/<path:filename>')
def serve_image(filename):
    image_full_path = os.path.join(BASE_IMAGES_PATH, filename)
    if os.path.exists(image_full_path):
        return send_file(image_full_path, mimetype='image/jpeg')
    return jsonify({"error": "Image not found"}), 404
