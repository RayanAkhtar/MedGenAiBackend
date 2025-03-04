import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

def process_csv():
    """Send a POST request to the /scripts/processCSV endpoint."""
    try:
        url = f"{BASE_URL}/scripts/processCSV"
        
        response = requests.post(url)

        if response.status_code == 200:
            print("CSV processed and images inserted successfully.")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    process_csv()
