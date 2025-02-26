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

def drop_tables():
    """Drops all tables from the database."""
    drop_queries = [
        "DROP TABLE IF EXISTS user_tags;",
        "DROP TABLE IF EXISTS tag;",
        "DROP TABLE IF EXISTS feedback_users;",
        "DROP TABLE IF EXISTS feedback;",
        "DROP TABLE IF EXISTS user_guesses;",
        "DROP TABLE IF EXISTS images;",
        "DROP TABLE IF EXISTS competition_users;",
        "DROP TABLE IF EXISTS users;",
        "DROP TABLE IF EXISTS competitions;"
    ]
    
    for query in drop_queries:
        response = execute_sql_query(query)
        if response.status_code == 200:
            print(f"Successfully dropped table: {query}")
        else:
            print(f"Failed to drop table: {query}, Error: {response.text}")

def create_tables():
    """Creates all tables in the database."""
    create_queries = [
        """
        CREATE TABLE competitions (
            competition_id SERIAL PRIMARY KEY,
            competition_name VARCHAR(100) NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL
        );
        """,
        """
        CREATE TABLE users (
            user_id VARCHAR(128) PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            level INT NOT NULL DEFAULT 1,
            exp INT NOT NULL DEFAULT 0,
            games_started INT NOT NULL DEFAULT 0,
            games_won INT NOT NULL DEFAULT 0,
            score INT NOT NULL DEFAULT 0,
            firebase_uid VARCHAR(128) NOT NULL
        );
        """,
        """
        CREATE TABLE competition_users (
            id SERIAL PRIMARY KEY,
            competition_id INT NOT NULL,
            user_id VARCHAR(128) NOT NULL,
            score INT NOT NULL,
            FOREIGN KEY (competition_id) REFERENCES competitions(competition_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """,
        """
        CREATE TABLE images (
            image_id SERIAL PRIMARY KEY,
            image_path VARCHAR(255) NOT NULL,
            image_type VARCHAR(50) NOT NULL,
            upload_time TIMESTAMP NOT NULL,
            gender VARCHAR(20),
            age INT,
            disease VARCHAR(50)
        );
        """,
        """
        CREATE TABLE user_guesses (
            guess_id SERIAL PRIMARY KEY,
            image_id INT NOT NULL,
            user_id VARCHAR(128) NOT NULL,
            user_guess_type VARCHAR(50) NOT NULL,
            date_of_guess TIMESTAMP NOT NULL,
            FOREIGN KEY (image_id) REFERENCES images(image_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """,
        """
        CREATE TABLE feedback (
            feedback_id SERIAL PRIMARY KEY,
            x INT NOT NULL,
            y INT NOT NULL,
            msg VARCHAR(255) NOT NULL,
            resolved BOOLEAN DEFAULT FALSE NOT NULL,
            date_added TIMESTAMP NOT NULL,
            confidence INT NOT NULL DEFAULT 50
        );
        """,
        """
        CREATE TABLE feedback_users (
            feedback_id INT PRIMARY KEY,
            guess_id INT NOT NULL,
            FOREIGN KEY (guess_id) REFERENCES user_guesses(guess_id)
        );
        """,
        """
        CREATE TABLE tag (
            tag_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL
        );
        """,
        """
        CREATE TABLE user_tags (
            user_id VARCHAR(128) NOT NULL,
            tag_id INT NOT NULL,
            PRIMARY KEY (user_id, tag_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (tag_id) REFERENCES tag(tag_id)
        );
        """
    ]
    
    for query in create_queries:
        response = execute_sql_query(query)
        if response.status_code == 200:
            print(f"Successfully created table: {query[:30]}...")
        else:
            print(f"Failed to create table: {query[:30]}..., Error: {response.text}")

if __name__ == "__main__":
    try:
        print("Dropping all tables...")
        drop_tables()
        print("All tables dropped successfully.")
        print("Creating tables...")
        create_tables()
        print("All tables created successfully.")
    except Exception as e:
        print(f"Error during table operations: {e}")
        raise
