import requests
from dotenv import load_dotenv
import os

load_dotenv()
BASE_URL = os.getenv("BASE_URL")

def execute_sql_query(query):
    """Helper function to send POST requests with a SQL query."""
    response = requests.post(
        BASE_URL + "execute_sql",
        json={"query": query},
        headers={"Content-Type": "application/json"}
    )
    print(f"Query: {query}")
    print(f"Response Status: {response.status_code}, Response Text: {response.text}")
    return response

def insert_test_data():
    """Insert sample data for all tables."""
    data_queries = [
        # Competitions
        """
        INSERT INTO competitions (competition_id, competition_name, start_date, end_date)
        VALUES
            (1, 'MedGen Challenge', '2025-01-01', '2025-12-31'),
            (2, 'AI Championship', '2025-06-15', '2025-09-01'),
            (3, 'Data Science Battle', '2024-03-01', '2024-06-30'),
            (4, 'Health Hackathon', '2023-11-01', '2024-01-15'),
            (5, 'Open Innovation Fest', '2024-05-10', '2024-12-20')
        ON CONFLICT (competition_id) DO NOTHING;
        """,

        # Users (Avoid duplicate insertions)
        """
        INSERT INTO users (user_id, username, level, exp, games_started, games_won, score)
        VALUES
            (1, 'test_user1', 1, 100, 5, 3, 120),
            (2, 'test_user2', 2, 150, 7, 5, 180),
            (3, 'test_user3', 3, 200, 8, 4, 220)
        ON CONFLICT (username) DO NOTHING;
        """,

        # Images
        """
        INSERT INTO images (image_id, image_path, image_type, upload_time, gender, age, disease)
        VALUES
            (111111, '/test_images/fake_1.jpg', 'ai', '2023-03-17', 'male', 55, 'none'),
            (111112, '/test_images/fake_2.jpg', 'real', '2023-03-17', 'none', 23, 'none'),
            (111113, '/test_images/fake_3.jpg', 'ai', '2023-03-17', 'none', 34, 'pleural effusion')
        ON CONFLICT (image_id) DO NOTHING;
        """,

        # User Guesses (Allow null session_id)
        """
        ALTER TABLE user_guesses ALTER COLUMN session_id DROP NOT NULL;
        """,
        """
        INSERT INTO user_guesses (guess_id, image_id, user_id, user_guess_type, date_of_guess, session_id)
        VALUES
            (1, 111111, 1, 'ai', '2024-02-01', NULL),
            (2, 111111, 2, 'real', '2024-02-02', NULL)
        ON CONFLICT (guess_id) DO NOTHING;
        """,

        # Feedback
        """
        INSERT INTO feedback (feedback_id, x, y, msg, resolved, date_added, confidence)
        VALUES
            (1, 0, 1, 'Great image quality', false, '2023-04-21', 5),
            (2, 1, 0, 'Background needs work', false, '2023-04-21', 10)
        ON CONFLICT (feedback_id) DO NOTHING;
        """,

        # Feedback Users
        """
        INSERT INTO feedback_users (guess_id, feedback_id)
        VALUES
            (1, 1),
            (2, 2)
        ON CONFLICT (feedback_id) DO NOTHING;
        """,

        # Competition Users
        """
        INSERT INTO competition_users (competition_id, user_id, score)
        VALUES
            (1, 1, 100),
            (1, 2, 150),
            (2, 3, 120)
        ON CONFLICT (id) DO NOTHING;
        """
    ]

    for query in data_queries:
        response = execute_sql_query(query)
        if response.status_code == 200:
            print(f"Data successfully inserted for query: {query[:30]}...")
        else:
            print(f"Failed to insert data: {response.text}")

def cleanup():
    """Safely delete all records using TRUNCATE with CASCADE."""
    query = """
    TRUNCATE TABLE feedback_users, feedback, user_tags, user_guesses, 
    competition_users, images, users, competitions, games 
    RESTART IDENTITY CASCADE;
    """
    response = execute_sql_query(query)
    print(f"Response Status: {response.status_code}, Response Text: {response.text}")

if __name__ == "__main__":
    try:
        cleanup()
        print("Inserting test data...")
        insert_test_data()
        print("Test data inserted successfully.")
    except Exception as e:
        print(f"Error during test data insertion: {e}")
        print("Cleaning up...")
        cleanup()
        raise
