import os
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv
from __init__ import db
from models import Users, UserGuess, Images, FeedbackUser, Feedback, Competition, Tag, UserTags, CompetitionUser


# Load environment variables
load_dotenv("../.env")
BASE_URL = os.getenv("BASE_URL")
CSV_FILE_PATH = "../MedGenAI-Images/Images/test_cfs.csv"
BATCH_SIZE = 500  # Inserting this many images at a time

COLUMNS_TO_PROCESS = [
    "path_cf_Male", "path_cf_Female", "path_cf_Null", "path_cf_No_disease", "path_cf_Pleural_Effusion"
]

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

# Function to drop all relevant tables
def drop_tables():
    try:
        # Drop all tables in the database
        db.drop_all()
        print("All tables have been dropped.")
    except Exception as e:
        print(f"An error occurred while dropping tables: {str(e)}")
        raise e
    


def batch_insert(records):
    """Insert records in batches."""
    total_records = len(records)
    for i in range(0, total_records, BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        values = ", ".join(
            f"('{path}', '{img_type}', '{upload_time}', "
            f"{'NULL' if gender is None else repr(gender)}, "
            f"{'NULL' if age is None else repr(age)}, "
            f"{'NULL' if disease is None else repr(disease)})"
            for img_id, path, img_type, upload_time, gender, race, age, disease in batch
        )
        query = f"""
        INSERT INTO images (image_path, image_type, upload_time, gender, age, disease)
        VALUES {values};
        """
        print("Query is: ", query)
        response = execute_sql_query(query)
        if response.status_code == 200:
            print(f"Successfully inserted {len(batch)} records.")
        else:
            print(f"Failed to insert batch, Error: {response.text}")


def process_csv():
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        df["id"] = df["id"] + 1  # Increment ID since csv starts from 0, but images start from 1
        image_records = []
        
        for _, row in df.iterrows():
            real_image_path = f"real_images/{row['id']}.jpg"
            image_records.append((row["id"], real_image_path, "real", datetime.now(), None, None, None, None))
            
            for col in COLUMNS_TO_PROCESS:
                if pd.notna(row[col]):
                    processed_path = "/".join(row[col].split("/")[-2:])
                    gender = "Male" if "Male" in col else "Female" if "Female" in col else None
                    disease = col.replace("path_cf_", "") if "path_cf_" in col else None
                    if disease in ["Male", "Female", "Null"]:
                        disease = None
                    
                    image_records.append((row["id"], processed_path, "ai", datetime.now(), gender, None, row["age"], disease))
        
        # Insert the processed image records into the database
        batch_insert(image_records)
    except Exception as e:
        print(f"Error processing CSV: {e}")


# Function to setup all tables (create them if they don't exist)
def setup_tables():
    try:
        # Create all the tables
        db.create_all()
        print("Tables created successfully.")
        
        # Populate the Images table using the CSV data
        process_csv()

    except Exception as e:
        print(f"An error occurred while setting up tables: {str(e)}")
        raise e


# Function to populate tables with initial data (you can define any initial data here)
def populate_tables():
    """Populate tables using SQL insert queries from the file."""
    try:
        # Define the SQL queries for inserting test data
        data_queries = [
            # Competitions
            """
            INSERT INTO competitions (competition_id, competition_name, start_date, end_date)
            VALUES 
                (1, 'MedGen Challenge', '2025-01-01', '2025-12-31'),
                (2, 'AI Championship', '2025-06-15', '2025-09-01'),
                (3, 'Data Science Battle', '2024-03-01', '2024-06-30'),
                (4, 'Health Hackathon', '2023-11-01', '2024-01-15'),
                (5, 'Open Innovation Fest', '2024-05-10', '2024-12-20');
            """,

            # Users
            """
            INSERT INTO users (user_id, username, level, exp, games_started, games_won, score)
            VALUES 
                (1, 'test_user1', 1, 100, 5, 3, 120),
                (2, 'test_user2', 2, 150, 7, 5, 180),
                (3, 'test_user3', 3, 200, 8, 4, 220);
            """,

            # Images
            """
            INSERT INTO images (image_id, image_path, image_type, upload_time, gender, age, disease)
            VALUES 
                (111111, '/test_images/fake_1.jpg', 'ai', '2023-03-17', 'male', 55, 'none'),
                (111112, '/test_images/fake_2.jpg', 'real', '2023-03-17', 'none', 23, 'none'),
                (111113, '/test_images/fake_3.jpg', 'ai', '2023-03-17', 'none', 34, 'pleural effusion');
            """,

            # User Guesses
            """
            INSERT INTO user_guesses (guess_id, image_id, user_id, user_guess_type, date_of_guess)
            VALUES 
                (1, 111111, 1, 'ai', '2024-02-01'),
                (2, 111111, 2, 'real', '2024-02-02'),
                (3, 111111, 3, 'ai', '2024-03-05'),
                (4, 111111, 1, 'real', '2024-04-12'),
                (5, 111111, 2, 'ai', '2024-04-20'),
                (6, 111112, 1, 'real', '2024-05-10'),
                (7, 111112, 3, 'ai', '2024-06-01'),
                (8, 111113, 2, 'real', '2024-07-15'),
                (9, 111113, 1, 'ai', '2024-08-23'),
                (10, 111111, 3, 'real', '2024-09-07'),
                (11, 111111, 2, 'ai', '2024-10-14'),
                (12, 111111, 1, 'real', '2024-11-03'),
                (13, 111112, 3, 'ai', '2024-12-10'),
                (14, 111112, 2, 'real', '2025-01-05'),
                (15, 111112, 1, 'ai', '2025-01-20'),
                (16, 111112, 3, 'real', '2025-02-01'),
                (17, 111113, 2, 'ai', '2025-02-07'),
                (18, 111113, 1, 'real', '2025-03-02'),
                (19, 111113, 3, 'ai', '2025-03-15'),
                (20, 111113, 2, 'real', '2025-04-10');
            """,

            # Feedback
            """
            INSERT INTO feedback (feedback_id, x, y, msg, resolved, date_added, confidence)
            VALUES 
                (1, 0, 1, 'Great image quality', false, '2023-04-21', 5),
                (2, 1, 0, 'Background needs work', false, '2023-04-21', 10),
                (3, 2, 3, 'Perfect edge detection', false, '2023-04-21', 23),
                (4, 3, 4, 'Blurry in corners', false, '2023-04-21', 54),
                (5, 4, 5, 'Noise in shadow areas', false, '2023-04-21', 56),
                (6, 0, 2, 'Too dark in some areas', false, '2023-04-21', 43),
                (7, 1, 4, 'Excellent contrast and detail', false, '2023-04-21', 76),
                (8, 2, 1, 'The lighting is too harsh on the subject', false, '2023-04-21', 54),
                (9, 3, 5, 'The colors are off in the shadows', false, '2023-04-21', 34),
                (10, 4, 2, 'The focus seems soft in the middle', false, '2023-04-21', 65),
                (11, 5, 1, 'Great use of depth of field', true, '2023-04-21', 76),
                (12, 6, 3, 'The image appears overexposed', false, '2023-04-21', 01),
                (13, 0, 4, 'Lack of clarity in details', true, '2023-04-21', 62),
                (14, 2, 2, 'Background feels too cluttered', false, '2023-04-21', 26),
                (15, 1, 5, 'Nice composition and symmetry', true, '2023-04-21', 93);
            """,

            # Feedback Users
            """
            INSERT INTO feedback_users (guess_id, feedback_id)
            VALUES 
                (1, 1),
                (2, 2),
                (3, 3),
                (4, 4),
                (5, 5),
                (1, 6),
                (2, 7),
                (1, 8),
                (2, 9),
                (1, 10),
                (2, 11),
                (1, 12),
                (2, 13),
                (2, 14),
                (1, 15);
            """,

            # Competition Users
            """
            INSERT INTO competition_users (competition_id, user_id, score)
            VALUES 
                (1, 1, 100),
                (1, 2, 150),
                (2, 3, 120),
                (3, 1, 300),
                (4, 1, 250),
                (5, 1, 200),
                (5, 1, 220);
            """
        ]
        
        # Execute all the queries
        for query in data_queries:
            response = execute_sql_query(query)
            if response.status_code == 200:
                print(f"Data successfully inserted for query: {query[:30]}...")
            else:
                print(f"Failed to insert data: {response.text}")
        
        print("Tables populated with initial data.")
    except Exception as e:
        print(f"An error occurred while populating tables: {str(e)}")
        raise e