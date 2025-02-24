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
        "DROP TABLE IF EXISTS images;",
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
        CREATE TABLE images (
            image_id SERIAL PRIMARY KEY,
            image_path VARCHAR(255) NOT NULL,
            image_type VARCHAR(50) NOT NULL,
            upload_time TIMESTAMP NOT NULL,
            gender VARCHAR(20),
            race VARCHAR(20),
            age INT,
            disease VARCHAR(50)
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
