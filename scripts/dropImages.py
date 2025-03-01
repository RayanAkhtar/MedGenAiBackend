import os
import sys
from pathlib import Path
import psycopg2
from datetime import datetime

# Database connection parameters - update these with your actual values
DB_PARAMS = {
    "dbname": "medgen",
    "user": "medgen_user",
    "password": "blackberry",
    "host": "localhost",
    "port": "5432"
}

# Constants
IMAGE_DIRECTORY = Path("../MedGenAI-Images/Images").resolve()
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
STARTING_ID = 100000

def execute_sql_query(query):
    """Execute SQL query directly using psycopg2."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Query executed successfully: {query[:100]}...")
        return True
    except psycopg2.errors.UniqueViolation:
        # Handle duplicate entries gracefully
        if conn:
            conn.rollback()
            conn.close()
        print(f"Skipping duplicate image")
        return True  # Consider duplicates as successful
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        print(f"Error executing query: {str(e)}")
        print(f"Failed query: {query}")
        return False

def verify_directory():
    """Verify that the image directory exists and is accessible."""
    if not IMAGE_DIRECTORY.exists():
        raise FileNotFoundError(f"Image directory not found: {IMAGE_DIRECTORY}")
    if not IMAGE_DIRECTORY.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {IMAGE_DIRECTORY}")
    print(f"Using image directory: {IMAGE_DIRECTORY}")

def get_image_type(path):
    """Determine if image is AI or real based on path."""
    path_str = str(path).lower()
    return "real" if "real_images" in path_str else "ai"

def setup_images():
    """Recursively add image files from the directory to the database."""
    try:
        verify_directory()
        
        # First, ensure the image_path column has a unique constraint
        create_constraint_query = """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint 
                WHERE conname = 'images_image_path_key' AND conrelid = 'images'::regclass
            ) THEN
                ALTER TABLE images ADD CONSTRAINT images_image_path_key UNIQUE (image_path);
            END IF;
        END
        $$;
        """
        execute_sql_query(create_constraint_query)
        
        image_data = []
        skipped_files = []

        # Collect all valid image files
        for file_path in IMAGE_DIRECTORY.rglob("*"):
            if file_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                try:
                    relative_path = file_path.relative_to(IMAGE_DIRECTORY)
                    db_image_path = f"/{relative_path}".replace("\\", "/")
                    image_type = get_image_type(relative_path)
                    image_data.append((db_image_path, image_type))
                except Exception as e:
                    skipped_files.append((file_path, str(e)))

        if not image_data:
            print("No valid images found in the specified directory.")
            return

        print(f"Found {len(image_data)} valid images")

        # Insert images into database
        successful_inserts = 0
        failed_inserts = 0

        for idx, (path, img_type) in enumerate(image_data, start=1):
            # Use a simpler query without ON CONFLICT
            query = f"""
            INSERT INTO images (image_id, image_path, image_type, upload_time)
            SELECT {STARTING_ID + idx}, '{path}', '{img_type}', CURRENT_DATE
            WHERE NOT EXISTS (
                SELECT 1 FROM images WHERE image_path = '{path}'
            );
            """
            if execute_sql_query(query):
                successful_inserts += 1
                print(f"Successfully inserted image {successful_inserts}/{len(image_data)}: {path}")
            else:
                failed_inserts += 1
                print(f"Failed to insert image: {path}")

        # Print summary
        print("\nImage Upload Summary:")
        print(f"Total images found: {len(image_data)}")
        print(f"Successfully inserted: {successful_inserts}")
        print(f"Failed to insert: {failed_inserts}")
        
        if skipped_files:
            print("\nSkipped files:")
            for file_path, error in skipped_files:
                print(f"- {file_path}: {error}")

    except Exception as e:
        print(f"Error during image setup: {str(e)}")
        raise

def main():
    try:
        print("Starting image setup...")
        setup_images()
        print("Image setup completed successfully.")
        return 0
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())