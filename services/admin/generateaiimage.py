import os
from flask import request, send_from_directory
from models import Images
from sqlalchemy.sql.expression import func

BASE_DIR = "../../MedGenAI-Images/Images"

def map_age_range(age_range):
    """
    Maps the provided age range string to a database query filter.
    """
    age_mapping = {
        "18-25": (18, 25),
        "26-35": (26, 35),
        "36-45": (36, 45),
        "46-60": (46, 60),
        "60+": (60, 120)  # Assuming max age is 120
    }
    
    return age_mapping.get(age_range, None)

def generate_image(age: str = "", gender: str = "", disease: str = ""):
    """
    Retrieves a random image from the database based on filters.
    
    Parameters:
    - age (str): The selected age range.
    - gender (str): The selected gender.
    - disease (str): The selected disease.
    
    Returns:
    - Response: The actual image (as a binary blob) to be displayed.
    """
    query = Images.query

    age = age if age else "any"
    gender = gender if gender else "any"
    disease = disease if disease else "any"


    if age != "any":
        age_range = map_age_range(age)
        if age_range:
            query = query.filter(Images.age.between(*age_range))
    if gender != "any":
        query = query.filter(Images.gender == gender)
    if disease != "any":
        query = query.filter(Images.disease == disease)

    # Get a random image that matches the filters
    image = query.order_by(func.random()).first()

    if image:
        image_path = image.image_path
        return send_from_directory(os.path.join(BASE_DIR, 'Generated'), image_path)

    return None
