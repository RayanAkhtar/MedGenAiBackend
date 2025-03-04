import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from __init__ import db
from models import Users, UserGuess, Images, FeedbackUser, Feedback, Competition, Tag, UserTags, CompetitionUser, Game, UserGameSession


load_dotenv("../.env")
CSV_FILE_PATH = "../MedGenAI-Images/Images/test_cfs.csv"
BATCH_SIZE = 500  # Inserting this many images at a time

COLUMNS_TO_PROCESS = [
    "path_cf_Male", "path_cf_Female", "path_cf_Null", "path_cf_No_disease", "path_cf_Pleural_Effusion"
]

def batch_insert(records):
    """Insert records in batches using SQLAlchemy."""
    total_records = len(records)
    for i in range(0, total_records, BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        for record in batch:
            image = Images(
                image_path=record[1],
                image_type=record[2],
                upload_time=record[3],
                gender=record[4],
                age=record[5],
                disease=record[6]
            )
            db.session.add(image)
        db.session.commit()
        print(f"Successfully inserted {len(batch)} records.")

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
        
        batch_insert(image_records)
    except Exception as e:
        print(f"Error processing CSV: {e}")

def drop_tables():
    try:
        db.drop_all()
        print("All tables have been dropped.")
    except Exception as e:
        print(f"An error occurred while dropping tables: {str(e)}")
        raise e

def setup_tables():
    try:
        db.create_all()
        print("Tables created successfully.")
        
        process_csv()

    except Exception as e:
        print(f"An error occurred while setting up tables: {str(e)}")
        raise e

def populate_tables():
    """Populate tables using SQLAlchemy insert."""
    try:
        users = [
            Users(user_id=1, username="test_user1", level=1, exp=100, games_started=5, games_won=3, score=120),
            Users(user_id=2, username="test_user2", level=2, exp=150, games_started=7, games_won=5, score=180),
            Users(user_id=3, username="test_user3", level=3, exp=200, games_started=8, games_won=4, score=220)
        ]
        
        db.session.add_all(users)
        
        db.session.commit()
        print("Users successfully inserted.")

        games = [
            Game(game_id=1, game_mode="Classic", date_created=datetime(2025, 1, 1), game_board="Standard", 
                 game_status="Active", expiry_date=datetime(2025, 12, 31), created_by=1),
            Game(game_id=2, game_mode="AI", date_created=datetime(2025, 6, 15), game_board="Advanced", 
                 game_status="Active", expiry_date=datetime(2025, 9, 1), created_by=2),
            Game(game_id=3, game_mode="Tournament", date_created=datetime(2024, 3, 1), game_board="Elite", 
                 game_status="Inactive", expiry_date=datetime(2024, 6, 30), created_by=3),
            Game(game_id=4, game_mode="Classic", date_created=datetime(2023, 11, 1), game_board="Standard", 
                 game_status="Active", expiry_date=datetime(2024, 1, 15), created_by=1),
            Game(game_id=5, game_mode="AI", date_created=datetime(2024, 5, 10), game_board="Advanced", 
                 game_status="Inactive", expiry_date=datetime(2024, 12, 20), created_by=2)
        ]
        
        db.session.add_all(games)
        
        db.session.commit()
        print("Games successfully inserted.")

        sessions = [
            UserGameSession(session_id=1, game_id=1, user_id=1, start_time=datetime(2024, 2, 1), end_time=datetime(2024, 2, 5)),
            UserGameSession(session_id=2, game_id=1, user_id=2, start_time=datetime(2024, 2, 2), end_time=datetime(2024, 2, 6)),
            UserGameSession(session_id=3, game_id=2, user_id=3, start_time=datetime(2024, 3, 1), end_time=datetime(2024, 3, 5)),
            UserGameSession(session_id=4, game_id=3, user_id=1, start_time=datetime(2024, 4, 1), end_time=datetime(2024, 4, 5)),
            UserGameSession(session_id=5, game_id=4, user_id=2, start_time=datetime(2024, 5, 1), end_time=datetime(2024, 5, 5)),
        ]
        
        db.session.add_all(sessions)
        db.session.commit()
        print("User game sessions successfully inserted.")

        competitions = [
            Competition(competition_id=1, competition_name="MedGen Challenge", start_date="2025-01-01", end_date="2025-12-31"),
            Competition(competition_id=2, competition_name="AI Championship", start_date="2025-06-15", end_date="2025-09-01"),
            Competition(competition_id=3, competition_name="Data Science Battle", start_date="2024-03-01", end_date="2024-06-30"),
            Competition(competition_id=4, competition_name="Health Hackathon", start_date="2023-11-01", end_date="2024-01-15"),
            Competition(competition_id=5, competition_name="Open Innovation Fest", start_date="2024-05-10", end_date="2024-12-20")
        ]
        
        db.session.add_all(competitions)
        
        db.session.commit()
        print("Competitions successfully inserted.")

        images = [
            Images(image_id=111111, image_path='/test_images/fake_1.jpg', image_type='ai', upload_time='2023-03-17', gender='male', age=55, disease='none'),
            Images(image_id=111112, image_path='/test_images/fake_2.jpg', image_type='real', upload_time='2023-03-17', gender=None, age=23, disease='none'),
            Images(image_id=111113, image_path='/test_images/fake_3.jpg', image_type='ai', upload_time='2023-03-17', gender=None, age=34, disease='pleural effusion')
        ]
        
        db.session.add_all(images)

        user_guesses = [
            UserGuess(guess_id=1, image_id=111111, user_id=1, user_guess_type='ai', date_of_guess='2024-02-01'),
            UserGuess(guess_id=2, image_id=111111, user_id=2, user_guess_type='real', date_of_guess='2024-02-02'),
            UserGuess(guess_id=3, image_id=111111, user_id=3, user_guess_type='ai', date_of_guess='2024-03-05'),
            UserGuess(guess_id=4, image_id=111111, user_id=1, user_guess_type='real', date_of_guess='2024-04-12'),
            UserGuess(guess_id=5, image_id=111111, user_id=2, user_guess_type='ai', date_of_guess='2024-04-20'),
            UserGuess(guess_id=6, image_id=111112, user_id=1, user_guess_type='real', date_of_guess='2024-05-10'),
            UserGuess(guess_id=7, image_id=111112, user_id=3, user_guess_type='ai', date_of_guess='2024-06-01'),
            UserGuess(guess_id=8, image_id=111113, user_id=2, user_guess_type='real', date_of_guess='2024-07-15'),
            UserGuess(guess_id=9, image_id=111113, user_id=1, user_guess_type='ai', date_of_guess='2024-08-23')
        ]
        
        db.session.add_all(user_guesses)

        feedback = [
            Feedback(feedback_id=1, x=0, y=1, msg='Great image quality', resolved=False, date_added='2023-04-21', confidence=5),
            Feedback(feedback_id=2, x=1, y=0, msg='Background needs work', resolved=False, date_added='2023-04-21', confidence=10),
            Feedback(feedback_id=3, x=2, y=3, msg='Perfect edge detection', resolved=False, date_added='2023-04-21', confidence=23),
            Feedback(feedback_id=4, x=3, y=4, msg='Blurry in corners', resolved=False, date_added='2023-04-21', confidence=54),
            Feedback(feedback_id=5, x=4, y=5, msg='Noise in shadow areas', resolved=False, date_added='2023-04-21', confidence=56),
            Feedback(feedback_id=6, x=0, y=2, msg='Too dark in some areas', resolved=False, date_added='2023-04-21', confidence=43)
        ]
        
        db.session.add_all(feedback)

        feedback_users = [
            FeedbackUser(guess_id=1, feedback_id=1),
            FeedbackUser(guess_id=2, feedback_id=2),
            FeedbackUser(guess_id=3, feedback_id=3),
            FeedbackUser(guess_id=4, feedback_id=4)
        ]
        
        db.session.add_all(feedback_users)

        competition_users = [
            CompetitionUser(competition_id=1, user_id=1, score=100),
            CompetitionUser(competition_id=1, user_id=2, score=150),
            CompetitionUser(competition_id=2, user_id=3, score=120)
        ]
        
        db.session.add_all(competition_users)

        db.session.commit()

        print("Tables populated with initial data.")
        
    except Exception as e:
        print(f"An error occurred while populating tables: {str(e)}")
        raise e
