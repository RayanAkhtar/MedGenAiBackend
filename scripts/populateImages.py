import os
import requests
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv("../.env")

# Get the BASE_URL from the environment variable
BASE_URL = os.getenv("BASE_URL")

def populate_tables():
    """Send a POST request to the /scripts/populateTables endpoint."""
    try:
        url = f"{BASE_URL}/scripts/populateTables"
        
        # Send POST request to the endpoint
        response = requests.post(url)

        # Check the response status code and handle accordingly
        if response.status_code == 200:
            print("Tables populated successfully.")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Run the populate_tables function when running the script
    populate_tables()
