import os
import re
from flask import request
from app import db
from models import Images

def extract_image_id(file_name):
    """
    Extracts the numeric prefix from the file name.
    """
    match = re.match(r'^(\d+)', file_name)
    return int(match.group(1)) if match else None

def populate_images_table():
    image_list = get_image_list()

    for relative_path, file_name in image_list:
        image_id = extract_image_id(file_name)
        if image_id is None:
            print(f"Skipping file without numeric prefix: {file_name}")
            continue

        existing_image = Images.query.get(image_id)
        if existing_image:
            print(f"Image with ID {image_id} already exists. Skipping: {file_name}")
            continue

        # Determine image type
        parent_directory = os.path.basename(os.path.dirname(relative_path))
        if parent_directory.startswith('cf_'):
            image_type = 'ai'
        else:
            image_type = 'real'

        # Add the image to the database
        image_record = Images(
            image_id=image_id,
            image_path=relative_path,
            image_type=image_type
        )
        db.session.add(image_record)

    # Commit the transaction
    try:
        db.session.commit()
        print("Images table populated successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error while populating the Images table: {e}")

if __name__ == '__main__':
    with app.app_context():
        populate_images_table()
