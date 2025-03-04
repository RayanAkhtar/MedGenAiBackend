import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from __init__ import db
from models import Users, UserGuess, Images, FeedbackUser, Feedback, Competition, Tag, UserTags, CompetitionUser, Game, UserGameSession
import random

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
        print("attempt reading csv path")
        df = pd.read_csv(CSV_FILE_PATH)
        print("df", df)
        df["id"] = df["id"] + 1  # Increment ID since csv starts from 0, but images start from 1
        image_records = []
        print("df is", df)
        
        for _, row in df.iterrows():
            print("a")
            real_image_path = f"real_images/{row['id']}.jpg"
            image_records.append((row["id"], real_image_path, "real", datetime.now(), None, None, None, None))
            
            for col in COLUMNS_TO_PROCESS:
                print("b")
                if pd.notna(row[col]):
                    processed_path = "/".join(row[col].split("/")[-2:])
                    gender = "Male" if "Male" in col else "Female" if "Female" in col else None
                    disease = col.replace("path_cf_", "") if "path_cf_" in col else None
                    if disease in ["Male", "Female", "Null"]:
                        disease = None
                    
                    image_records.append((row["id"], processed_path, "ai", datetime.now(), gender, None, row["age"], disease))
        print("c")
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

def generate_random_date(start_year, end_year):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    delta = end_date - start_date
    random_day = random.randint(0, delta.days)
    random_date = start_date + timedelta(days=random_day)
    return random_date

def generate_hundreds_of_user_guesses_with_feedback(num_guesses=500):
    user_guesses = []
    feedback = []
    feedback_users = []
    
    for i in range(1, num_guesses + 1):
        session_id = random.randint(1, 5) 
        image_id = random.choice([111111, 111112, 111113])
        user_id = random.randint(1, 3)
        user_guess_type = random.choice(['ai', 'real'])
        date_of_guess = generate_random_date(2023, 2025)

        user_guess = UserGuess(
            guess_id=i, 
            session_id=session_id, 
            image_id=image_id, 
            user_id=user_id, 
            user_guess_type=user_guess_type, 
            date_of_guess=date_of_guess
        )
        user_guesses.append(user_guess)
        
        x, y = random.randint(0, 5), random.randint(0, 5)
        msg = random.choice([
            'Great image quality', 'Blurry in some areas', 'Perfect edge detection',
            'Too dark in some areas', 'Background needs work', 'Noise in shadow areas'
        ])
        resolved = random.choice([True, False])
        date_added = generate_random_date(2023, 2025)
        confidence = random.randint(1, 60)

        feedback_entry = Feedback(
            feedback_id=i, 
            x=x, 
            y=y, 
            msg=msg, 
            resolved=resolved, 
            date_added=date_added, 
            confidence=confidence
        )
        feedback.append(feedback_entry)
        
        feedback_user = FeedbackUser(guess_id=i, feedback_id=i)
        feedback_users.append(feedback_user)

    return user_guesses, feedback, feedback_users

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
            UserGameSession(session_id=1, game_id=1, user_id=1, start_time=datetime(2024, 2, 1), completion_time=datetime(2024, 2, 5),
                            session_status="completed", final_score=120, correct_guesses=10, total_guesses=12, time_taken=240),
            UserGameSession(session_id=2, game_id=1, user_id=2, start_time=datetime(2024, 2, 2), completion_time=datetime(2024, 2, 6),
                            session_status="completed", final_score=150, correct_guesses=13, total_guesses=15, time_taken=300),
            UserGameSession(session_id=3, game_id=2, user_id=3, start_time=datetime(2024, 3, 1), completion_time=datetime(2024, 3, 5),
                            session_status="completed", final_score=140, correct_guesses=12, total_guesses=15, time_taken=270),
            UserGameSession(session_id=4, game_id=3, user_id=1, start_time=datetime(2024, 4, 1), completion_time=datetime(2024, 4, 5),
                            session_status="completed", final_score=110, correct_guesses=9, total_guesses=12, time_taken=240),
            UserGameSession(session_id=5, game_id=4, user_id=2, start_time=datetime(2024, 5, 1), completion_time=datetime(2024, 5, 5),
                            session_status="completed", final_score=130, correct_guesses=11, total_guesses=14, time_taken=260)
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
            Images(image_id=111111, image_path='/test_images/fake_1.jpg', image_type='ai', 
                   upload_time=datetime(2023, 3, 17), gender='male', age=55, disease='none'),
            Images(image_id=111112, image_path='/test_images/fake_2.jpg', image_type='real', 
                   upload_time=datetime(2023, 3, 17), gender=None, age=23, disease='none'),
            Images(image_id=111113, image_path='/test_images/fake_3.jpg', image_type='ai', 
                   upload_time=datetime(2023, 3, 17), gender=None, age=34, disease='pleural effusion')
        ]
        
        db.session.add_all(images)
        db.session.commit()
        print("Images successfully inserted.")

        user_guesses, feedback_entries, feedback_users_entries = generate_hundreds_of_user_guesses_with_feedback(num_guesses=500)  # Generate 500 user guesses with feedback
        db.session.add_all(user_guesses)
        db.session.add_all(feedback_entries)
        db.session.add_all(feedback_users_entries)
        db.session.commit()
        print(f"{len(user_guesses)} UserGuesses and {len(feedback_entries)} Feedbacks successfully inserted.")

        competition_users = [
            CompetitionUser(competition_id=1, user_id=1, score=100),
            CompetitionUser(competition_id=1, user_id=2, score=150),
            CompetitionUser(competition_id=2, user_id=3, score=120)
        ]
        
        db.session.add_all(competition_users)
        db.session.commit()
        print("Competition Users successfully inserted.")

        print("Tables populated with initial data.")
        
    except Exception as e:
        print(f"An error occurred while populating tables: {str(e)}")
        raise e