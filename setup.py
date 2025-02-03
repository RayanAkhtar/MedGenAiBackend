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
        INSERT INTO images (image_path, image_type)
        VALUES 
            ('/images_get/static/images/real/1_Pleural_Effusion.jpg', 'real'),
            ('/images_get/static/images/real/2_Lung_Cancer.jpg', 'real'),
            ('/images_get/static/images/real/3_Tuberculosis.jpg', 'real'),
            ('/images_get/static/images/real/4_Pneumonia.jpg', 'real'),
            ('/images_get/static/images/real/5_Bronchitis.jpg', 'real'),
            ('/images_get/static/images/real/6_Asthma.jpg', 'real'),
            ('/images_get/static/images/real/7_Emphysema.jpg', 'real'),
            ('/images_get/static/images/real/8_Interstitial_Lung_Disease.jpg', 'real'),
            ('/images_get/static/images/real/9_Fibrosis.jpg', 'real'),
            ('/images_get/static/images/real/10_ARDS.jpg', 'real'),
            ('/images_get/static/images/real/11_Sarcoidosis.jpg', 'real'),
            ('/images_get/static/images/real/12_Cystic_Fibrosis.jpg', 'real'),
            ('/images_get/static/images/real/13_Sleep_Apnea.jpg', 'real'),
            ('/images_get/static/images/real/14_Obstructive_Lung_Disease.jpg', 'real'),
            ('/images_get/static/images/real/15_Lung_Infection.jpg', 'real'),
            ('/images_get/static/images/real/16_Lung_Embolism.jpg', 'real'),
            ('/images_get/static/images/real/17_Chest_Infection.jpg', 'real'),
            ('/images_get/static/images/real/18_Bronchiolitis.jpg', 'real'),
            ('/images_get/static/images/real/19_Empyema.jpg', 'real'),
            ('/images_get/static/images/real/20_Pneumothorax.jpg', 'real'),
            ('/images_get/static/images/real/21_Pulmonary_Fibrosis.jpg', 'real'),
            ('/images_get/static/images/real/22_Lung_Failure.jpg', 'real'),
            ('/images_get/static/images/real/23_Lung_Abscess.jpg', 'real'),
            ('/images_get/static/images/real/24_Pulmonary_Hypertension.jpg', 'real');
        """,
        
        # User Guesses (Updated: Corrected types and added more data)
        """
        INSERT INTO user_guesses (image_id, user_id, user_guess_type, date_of_guess)
        VALUES 
            (1, 1, 'real', '2025-02-01'),
            (2, 2, 'ai', '2025-02-02'),
            (3, 3, 'real', '2025-02-03'),
            (4, 4, 'ai', '2025-02-04'),
            (5, 5, 'real', '2025-02-05'),
            (6, 6, 'ai', '2025-02-06'),
            (7, 7, 'real', '2025-02-07');
        """,
        
        # Feedback (Updated: Added more feedback)
        """
        INSERT INTO feedback (feedback_id, x, y, msg, resolved)
        VALUES 
            (1, 0, 1, 'Great image quality', 1),
            (2, 1, 0, 'Background needs work', 0),
            (3, 2, 3, 'Perfect edge detection', 1),
            (4, 3, 4, 'Blurry in corners', 0),
            (5, 4, 5, 'Noise in shadow areas', 1),
            (6, 0, 2, 'Too dark in some areas', 0),
            (7, 1, 4, 'Excellent contrast and detail', 1),
            (8, 2, 1, 'The lighting is too harsh on the subject', 0),
            (9, 3, 5, 'The colors are off in the shadows', 1),
            (10, 4, 2, 'The focus seems soft in the middle', 0),
            (11, 5, 1, 'Great use of depth of field', 1),
            (12, 6, 3, 'The image appears overexposed', 0),
            (13, 0, 4, 'Lack of clarity in details', 1),
            (14, 2, 2, 'Background feels too cluttered', 0),
            (15, 1, 5, 'Nice composition and symmetry', 1);
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
