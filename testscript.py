import requests
import json

# Base URL for the Heroku app
BASE_URL = "https://med-gen-ai-backend-c632db28528e.herokuapp.com/execute_sql"

# Function to send POST requests with a SQL query
def execute_sql_query(query):
    response = requests.post(
        BASE_URL,
        json={"query": query},
        headers={"Content-Type": "application/json"}
    )
    return response

# Test 1: Test API connection with a simple select query
def test_connection():
    query = "SELECT 1;"
    response = execute_sql_query(query)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    print("Connection test passed.")

# Test 2: Insert data into the competitions table
def test_insert_data():
    query = """
    INSERT INTO competitions (name, start_date, end_date)
    VALUES ('MedGen Challenge', '2025-01-01', '2025-12-31');
    """
    response = execute_sql_query(query)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert response.json().get("message") == "Query executed successfully", "Insert failed"
    print("Data insertion test passed.")

# Test 3: Select data from the competitions table
def test_select_data():
    query = "SELECT * FROM competitions;"
    response = execute_sql_query(query)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check if response contains the inserted competition
    competitions = response.json()
    assert isinstance(competitions, list), "Expected list of competitions"
    assert len(competitions) > 0, "No competitions found"
    assert "name" in competitions[0], "Competition name missing in response"
    print("Data selection test passed.")

# Test 4: Update data in the competitions table
def test_update_data():
    query = """
    UPDATE competitions
    SET name = 'MedGen World Championship'
    WHERE name = 'MedGen Challenge';
    """
    response = execute_sql_query(query)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert response.json().get("message") == "Query executed successfully", "Update failed"
    print("Data update test passed.")

# Test 5: Delete data from the competitions table
def test_delete_data():
    query = """
    DELETE FROM competitions WHERE name = 'MedGen World Championship';
    """
    response = execute_sql_query(query)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert response.json().get("message") == "Query executed successfully", "Delete failed"
    print("Data deletion test passed.")

# Run all tests
if __name__ == "__main__":
    print("Starting tests...")
    test_connection()
    test_insert_data()
    test_select_data()
    test_update_data()
    test_delete_data()
    print("All tests passed!")
