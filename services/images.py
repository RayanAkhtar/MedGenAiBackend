import os
from flask import request

# Dynamically construct the path to the Images directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../MedGenAI-Images/Images"))

def get_relative_paths():
    """
    Returns a list of full image URLs for all images in the Images directory.
    """
    paths = []
    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):  # Supported image formats
                # Calculate relative path for the image
                relative_path = os.path.relpath(os.path.join(root, file), BASE_DIR)
                paths.append(f"{relative_path.replace(os.sep, '/')}")
    return paths

def get_image_list():
    """
    Returns a list of full image URLs for all images in the Images directory.
    """
    return [
        f"{request.host_url}api/images/view/{relative_path}"
        for relative_path in get_relative_paths()
    ]


def get_image_url(image_name):
    """
    Returns the full URL for a specific image by name, if it exists.
    """
    for root, _, files in os.walk(BASE_DIR):
        if image_name in files:
            # Calculate relative path for the image
            relative_path = os.path.relpath(os.path.join(root, image_name), BASE_DIR)
            # Generate the full URL dynamically
            return f"{request.host_url}api/images/view/{relative_path.replace(os.sep, '/')}"
    return None
