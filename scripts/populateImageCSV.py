import os
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
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

def process_csv():
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        df["id"] = df["id"] + 1  # Increment ID since csv starts from 0, but images start from 1
        image_records = []
        
        for _, row in df.iterrows():
            real_image_path = f"real_images/{row['id']}"
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

def batch_insert(records):
    """Insert records in batches."""
    total_records = len(records)
    for i in range(0, total_records, BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        values = ", ".join(
            f"({img_id}, '{path}', '{img_type}', '{upload_time}', {repr(gender)}, {repr(race)}, {repr(age)}, {repr(disease)})"
            for img_id, path, img_type, upload_time, gender, race, age, disease in batch
        )
        query = f"""
        INSERT INTO images (image_id, image_path, image_type, upload_time, gender, race, age, disease)
        VALUES {values};
        """
        response = execute_sql_query(query)
        if response.status_code == 200:
            print(f"Successfully inserted {len(batch)} records.")
        else:
            print(f"Failed to insert batch, Error: {response.text}")

if __name__ == "__main__":
    process_csv()