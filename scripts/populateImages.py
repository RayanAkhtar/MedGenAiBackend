import os
import requests
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL")

IMAGE_DIRECTORY = "../MedGenAI-Images/Images"
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}


def execute_sql_query(query):
    """Helper function to send POST requests with a SQL query."""
    response = requests.post(
        BASE_URL + "execute_sql",
        json={"query": query},
        headers={"Content-Type": "application/json"}
    )
    print(f"Query: {query[:50]}...")
    print(f"Response Status: {response.status_code}, Response Text: {response.text}")
    return response


def setup_images():
    """Recursively add image files from the directory to the database."""
    image_data = []

    for root, _, files in os.walk(IMAGE_DIRECTORY):
        for file_name in files:
            if any(file_name.lower().endswith(ext) for ext in SUPPORTED_IMAGE_EXTENSIONS):
                relative_path = os.path.relpath(root, IMAGE_DIRECTORY)
                db_image_path = f"/{relative_path}/{file_name}".replace("\\", "/")
                image_type = "ai" if not relative_path.startswith("real_images") else "real"
                upload_time = "CURRENT_DATE"

                image_data.append((db_image_path, image_type, upload_time))

    if not image_data:
        print("No images found in the specified directory.")
        return

    for idx, (path, img_type, upload_date) in enumerate(image_data, start=1):
        query = f"""
        INSERT INTO images (image_id, image_path, image_type, upload_time)
        VALUES ({100000 + idx}, '{path}', '{img_type}', {upload_date});
        """
        response = execute_sql_query(query)

        if response.status_code == 200:
            print(f"Successfully inserted image: {path}")
        else:
            print(f"Failed to insert image: {path}, Error: {response.text}")


if __name__ == "__main__":
    try:
        print("Setting up images...")
        setup_images()
        print("Image setup completed.")
    except Exception as e:
        print(f"Error during image setup: {e}")