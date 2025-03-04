import os
from flask import request, jsonify, send_file, url_for
from sqlalchemy import or_
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
    
    gender_condition = (Images.gender == gender) if gender and gender != "any" else None
    disease_condition = (Images.disease == disease) if disease and disease != "any" else None

    if gender_condition or disease_condition:
        query = query.filter(or_(gender_condition, disease_condition))

    image = query.order_by(func.random()).first()

    if image:
        image_path = image.image_path
        image_url = url_for('adminGenerate.serve_image', filename=image_path, _external=True)

        return jsonify({
            "imagePath": image_url
        })

    return jsonify({"error": "No matching image found"}), 404


