import os
import re
from datetime import datetime
from flask import request
from __init__ import db, create_app
from models import Images
from services.images import get_relative_paths

def extract_image_id(file_name):
    """
    Extracts the numeric prefix from the file name.
    """
    match = re.match(r'^(\d+)', file_name)
    return int(match.group(1)) if match else None

def populate_images_table():
    for relative_path in get_relative_paths():
        # Determine image type
        parent_directory = os.path.basename(os.path.dirname(relative_path))
        image_type = 'ai' if parent_directory.startswith('cf_') else 'real'

        # Add the image to the database
        image_record = Images(
            image_path=relative_path,
            image_type=image_type,
            upload_time = datetime.utcnow()
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
    app = create_app()

    with app.app_context():
        populate_images_table()
