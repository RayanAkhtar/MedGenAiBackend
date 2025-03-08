import os
import random
from flask import request, jsonify, send_file, url_for
from sqlalchemy import or_
from models import Images
from sqlalchemy.sql.expression import func

BASE_IMAGES_PATH = os.path.abspath(os.path.join(os.getcwd(), "../MedGenAI-Images/Images"))
CF_FOLDERS = {
    'Female': 'cf_Female',
    'Male': 'cf_Male',
    'None': 'cf_No_disease',
    'Pleural_Effusion': 'cf_Pleural_Effusion'
}
REAL_IMAGES_PATH = os.path.join(BASE_IMAGES_PATH, 'real_images')

def map_age_range(age_range):
    age_mapping = {
        "18-25": (18, 25),
        "26-35": (26, 35),
        "36-45": (36, 45),
        "46-60": (46, 60),
        "60+": (60, 120)
    }
    return age_mapping.get(age_range, None)

def check_folder_for_image(folder_name, file_name):
    folder_path = os.path.join(BASE_IMAGES_PATH, folder_name)
    file_path = os.path.join(folder_path, file_name)
    if os.path.exists(file_path):
        return file_path
    return None

def get_real_image_based_on_sex_or_disease(gender: str, disease: str, file_name: str):
    """
    Check the corresponding folder for a real image based on the gender or disease
    If the file exists, return the path, else return None.
    """
    folder = None

    if gender and gender != "any":
        folder = CF_FOLDERS.get(gender)

    elif disease and disease != "any":
        folder = CF_FOLDERS.get(disease)

    if folder:
        image_path = check_folder_for_image(folder, file_name)
        if image_path:
            image_url = url_for('adminGenerate.serve_image', filename=os.path.join(folder, file_name), _external=True)
            return jsonify({
                "imagePath": image_url,
                "fileName": file_name
            })
    
    return None

def generate_image(age: str = "", gender: str = "", disease: str = "", real_image_file_name: str = None):
    query = Images.query

    if age and age != "any":
        age_range = map_age_range(age)
        if age_range:
            query = query.filter(Images.age.between(*age_range))
    
    gender_condition = (Images.gender == gender) if gender and gender != "any" else None
    disease_condition = (Images.disease == disease) if disease and disease != "any" else None

    if gender_condition or disease_condition:
        query = query.filter(or_(gender_condition, disease_condition))

    if real_image_file_name and (gender != "any" or age != "any" or disease != "any"):
        return get_real_image_based_on_sex_or_disease(gender, disease, real_image_file_name)

    image = query.first()
    if image:
        file_name = f"{image.image_id}.jpg"

        selected_folder = None
        if gender and gender != "any":
            selected_folder = CF_FOLDERS.get(gender)
        elif disease and disease != "any":
            selected_folder = CF_FOLDERS.get(disease)

        if selected_folder:
            image_path = check_folder_for_image(selected_folder, file_name)
            if image_path:
                image_url = url_for('adminGenerate.serve_image', filename=os.path.join(selected_folder, file_name), _external=True)
                return jsonify({"imagePath": image_url})

    image = query.order_by(func.random()).first()

    if image:
        image_path = image.image_path
        image_url = url_for('adminGenerate.serve_image', filename=image_path, _external=True)
        return jsonify({
            "imagePath": image_url
        })

    return jsonify({"error": "No matching image found"}), 404
