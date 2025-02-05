import requests

BASE_URL = "http://127.0.0.1:5328/"

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
        INSERT INTO competitions (competition_name, start_date, end_date)
        VALUES 
            ('MedGen Challenge', '2025-01-01', '2025-12-31'),
            ('AI Championship', '2025-06-15', '2025-09-01'),
            ('Data Science Battle', '2024-03-01', '2024-06-30'),
            ('Health Hackathon', '2023-11-01', '2024-01-15'),
            ('Open Innovation Fest', '2024-05-10', '2024-12-20');
        """,
        
        # Users
        """
        INSERT INTO users (username, level, exp, games_started, games_won, score)
        VALUES 
            ('test_user1', 1, 100, 5, 3, 120),
            ('test_user2', 2, 150, 7, 5, 180),
            ('test_user3', 3, 200, 8, 4, 220),
            ('test_user4', 4, 350, 15, 12, 300),
            ('test_user5', 5, 500, 20, 18, 450),
            ('test_user6', 1, 90, 3, 1, 50),
            ('test_user7', 3, 250, 10, 6, 200);
        """,
        
        # Images (Updated paths to match the real images with "cf_" followed by condition names)
        """
        INSERT INTO images (image_path, image_type, upload_time)
        VALUES 
            ('/images_get/static/images/real/1_cf_Pleural_Effusion.jpg', 'ai', '2023-03-17'),
            ('/images_get/static/images/real/2_cf_Pleural_Effusion.jpg', 'real', '2023-03-17'),
            ('/images_get/static/images/real/3_cf_Pleural_Effusion.jpg', 'ai', '2023-03-17'),
            ('/images_get/static/images/real/4_cf_Pleural_Effusion.jpg', 'real', '2023-03-17'),
            ('/images_get/static/images/real/5_cf_Pleural_Effusion.jpg', 'real', '2023-03-13'),
            ('/images_get/static/images/real/6_cf_Pleural_Effusion.jpg', 'real', '2023-03-17'),
            ('/images_get/static/images/real/7_cf_Pleural_Effusion.jpg', 'real', '2023-03-16'),
            ('/images_get/static/images/real/8_cf_Pleural_Effusion.jpg', 'ai', '2023-03-14'),
            ('/images_get/static/images/real/9_cf_Pleural_Effusion.jpg', 'real', '2023-03-17'),
            ('/images_get/static/images/real/10_cf_Pleural_Effusion.jpg', 'real', '2023-03-17'),
            ('/images_get/static/images/real/11_cf_Pleural_Effusion.jpg', 'ai', '2023-03-12'),
            ('/images_get/static/images/real/12_cf_Pleural_Effusion.jpg', 'real', '2023-03-21'),
            ('/images_get/static/images/real/13_cf_Pleural_Effusion.jpg', 'real', '2023-03-17'),
            ('/images_get/static/images/real/14_cf_Pleural_Effusion.jpg', 'real', '2023-03-11'),
            ('/images_get/static/images/real/15_cf_Pleural_Effusion.jpg', 'ai', '2023-03-17'),
            ('/images_get/static/images/real/16_cf_Pleural_Effusion.jpg', 'real', '2023-03-12'),
            ('/images_get/static/images/real/17_cf_Pleural_Effusion.jpg', 'real', '2023-03-17'),
            ('/images_get/static/images/real/18_cf_Pleural_Effusion.jpg', 'ai', '2023-03-17'),
            ('/images_get/static/images/real/19_cf_Pleural_Effusion.jpg', 'real', '2023-03-13'),
            ('/images_get/static/images/real/20_cf_Pleural_Effusion.jpg', 'real', '2023-03-17'),
            ('/images_get/static/images/real/21_cf_Pleural_Effusion.jpg', 'real', '2023-03-14'),
            ('/images_get/static/images/real/22_cf_Pleural_Effusion.jpg', 'real', '2023-03-15'),
            ('/images_get/static/images/real/23_cf_Pleural_Effusion.jpg', 'ai', '2023-03-16'),
            ('/images_get/static/images/real/24_cf_Pleural_Effusion.jpg', 'real', '2023-03-18');
        """,
        
        # User Guesses (Updated: Corrected types and added more data)
        """
        INSERT INTO user_guesses (image_id, user_id, user_guess_type, date_of_guess)
        VALUES 
            -- Early 2024 (Fewer entries)
    (1, 1, 'ai', '2024-02-01'),
    (2, 2, 'ai', '2024-02-02'),
    (3, 3, 'real', '2024-03-05'),
    
    -- Mid 2024 (More entries)
    (4, 4, 'ai', '2024-04-12'),
    (5, 5, 'real', '2024-04-20'),
    (6, 6, 'ai', '2024-04-22'),
    (7, 7, 'real', '2024-05-03'),
    (1, 1, 'ai', '2024-05-06'),
    (2, 2, 'real', '2024-05-10'),
    (3, 3, 'ai', '2024-05-14'),
    (4, 4, 'real', '2024-06-01'),
    (5, 5, 'ai', '2024-06-08'),
    (6, 6, 'real', '2024-06-10'),
    (7, 7, 'ai', '2024-06-15'),
    (1, 1, 'real', '2024-07-01'),
    (2, 2, 'ai', '2024-07-03'),
    (3, 3, 'real', '2024-07-10'),
    (4, 4, 'ai', '2024-07-14'),
    (5, 5, 'real', '2024-07-21'),
    (6, 6, 'ai', '2024-07-28'),
    (7, 7, 'real', '2024-08-02'),
    
    -- Late 2024 (More entries)
    (1, 1, 'ai', '2024-09-05'),
    (2, 2, 'real', '2024-09-09'),
    (3, 3, 'ai', '2024-09-12'),
    (4, 4, 'real', '2024-09-17'),
    (5, 5, 'ai', '2024-10-01'),
    (6, 6, 'real', '2024-10-10'),
    (7, 7, 'ai', '2024-10-15'),
    (1, 1, 'real', '2024-11-01'),
    (2, 2, 'ai', '2024-11-05'),
    (3, 3, 'real', '2024-11-12'),
    (4, 4, 'ai', '2024-11-16'),
    (5, 5, 'real', '2024-11-22'),
    (6, 6, 'ai', '2024-11-27'),
    (7, 7, 'real', '2024-12-02'),
    (1, 1, 'ai', '2024-12-07'),
    
    -- Early 2025 (Fewer entries)
    (2, 2, 'real', '2025-01-10'),
    (3, 3, 'ai', '2025-01-13'),
    (4, 4, 'real', '2025-01-20'),
    (5, 5, 'ai', '2025-01-22'),
    (6, 6, 'real', '2025-02-05'),
    (7, 7, 'ai', '2025-02-10'),
    (1, 1, 'real', '2025-02-12'),
    (2, 2, 'ai', '2025-02-15');
        """,
        
        # Feedback (Updated: Added more feedback)
        """
        INSERT INTO feedback (feedback_id, x, y, msg, resolved, date_added)
        VALUES 
            (1, 0, 1, 'Great image quality', 1, '2023-04-21'),
            (2, 1, 0, 'Background needs work', 0, '2023-04-21'),
            (3, 2, 3, 'Perfect edge detection', 1, '2023-04-21'),
            (4, 3, 4, 'Blurry in corners', 0, '2023-04-21'),
            (5, 4, 5, 'Noise in shadow areas', 1, '2023-04-21'),
            (6, 0, 2, 'Too dark in some areas', 0, '2023-04-21'),
            (7, 1, 4, 'Excellent contrast and detail', 1, '2023-04-21'),
            (8, 2, 1, 'The lighting is too harsh on the subject', 0, '2023-04-21'),
            (9, 3, 5, 'The colors are off in the shadows', 1, '2023-04-21'),
            (10, 4, 2, 'The focus seems soft in the middle', 0, '2023-04-21'),
            (11, 5, 1, 'Great use of depth of field', 1, '2023-04-21'),
            (12, 6, 3, 'The image appears overexposed', 0, '2023-04-21'),
            (13, 0, 4, 'Lack of clarity in details', 1, '2023-04-21'),
            (14, 2, 2, 'Background feels too cluttered', 0, '2023-04-21'),
            (15, 1, 5, 'Nice composition and symmetry', 1, '2023-04-21');
        """,
        
        # Feedback Users (Updated: Added more feedback-users links)
        """
        INSERT INTO feedback_users (guess_id, feedback_id)
        VALUES 
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8),
            (9, 9),
            (10, 10),
            (11, 11),
            (12, 12),
            (13, 13),
            (14, 14),
            (15, 15);
        """,
        
        # Competition Users (Updated: Added more users to competitions)
        """
        INSERT INTO competition_users (competition_id, user_id, score)
        VALUES 
            (1, 1, 100),
            (1, 2, 150),
            (2, 3, 120),
            (3, 4, 300),
            (4, 5, 250),
            (5, 6, 200),
            (5, 7, 220);
        """
    ]
    
    for query in data_queries:
        response = execute_sql_query(query)
        if response.status_code == 200:
            print(f"Data successfully inserted for query: {query[:30]}...")
        else:
            print(f"Failed to insert data: {response.text}")




def cleanup():
    """Delete all records in tables."""
    queries = [
        "DELETE FROM competition_users;",
        "DELETE FROM feedback_users;",
        "DELETE FROM feedback;",
        "DELETE FROM user_guesses;",
        "DELETE FROM images;",
        "DELETE FROM users;",
        "DELETE FROM competitions;"
    ]
    for query in queries:
        response = execute_sql_query(query)
        if response.status_code == 200:
            print(f"Successfully cleared data from table: {query}")
        else:
            print(f"Failed to clear table data: {query}, Error: {response.text}")


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
