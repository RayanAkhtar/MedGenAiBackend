import requests

BASE_URL = "http://172.30.16.21:5328/"


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


def cleanup(): 
    """Delete all records in tables."""
    queries = [
        "DELETE FROM competitions;",
        "DELETE FROM users;",
        "DELETE FROM images;",
        "DELETE FROM user_guesses;"
    ]
    for query in queries:
        response = execute_sql_query(query)
        if response.status_code == 200:
            print(f"Successfully cleared data from table: {query}")
        else:
            print(f"Failed to clear table data: {query}, Error: {response.text}")


def run_tests():
    """Run all tests and clean up if an error occurs."""
    try:
        print("Starting tests...")
        test_initial()
        test_connection()
        test_insert_data_competitions()
        test_insert_data_users()
        test_insert_data_images()
        test_insert_data_user_guess()
        test_select_data_competitions()
        test_update_data_competitions()
        test_delete_data_competitions()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        print("Cleaning up records...")
        cleanup()
        raise


def test_initial():
    """Test basic API connection by making a simple GET request."""
    response = requests.get(BASE_URL + "hello")
    if response.ok:
        print("Response is:", response.json())
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
    return response


def test_connection():
    """Test API connection with a simple SELECT query."""
    query = "SELECT 1;"
    response = execute_sql_query(query)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    print("Connection test passed.")


def test_insert_data_competitions():
    query = """
    INSERT INTO competitions (competition_name, start_date, end_date)
    VALUES ('MedGen Challenge', '2025-01-01', '2025-12-31');
    """
    response = execute_sql_query(query)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert response.json().get("message") == "Query executed successfully", "Insert failed"
    print("Data insertion test (Competitions) passed.")


def test_insert_data_users():
    query = """
    INSERT INTO users (username, level, exp, games_started, games_won, score)
    VALUES ('test_user', 1, 0, 0, 0, 100);
    """
    response = execute_sql_query(query)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert response.json().get("message") == "Query executed successfully", "Insert failed"
    print("Data insertion test (Users) passed.")


def test_insert_data_images():
    query = """
    INSERT INTO images (image_path, image_type)
    VALUES ('/path/to/image.jpg', 'png');
    """
    response = execute_sql_query(query)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert response.json().get("message") == "Query executed successfully", "Insert failed"
    print("Data insertion test (Images) passed.")


def test_insert_data_user_guess():
    query = """
    INSERT INTO user_guesses (image_id, user_id, user_guess_type, date_of_guess)
    VALUES (1, 1, 'correct', '2025-02-01');
    """
    response = execute_sql_query(query)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert response.json().get("message") == "Query executed successfully", "Insert failed"
    print("Data insertion test (UserGuess) passed.")


def test_select_data_competitions():
    query = "SELECT * FROM competitions;"
    response = execute_sql_query(query)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    competitions = response.json()
    assert isinstance(competitions, list), "Expected list of competitions"
    assert len(competitions) > 0, "No competitions found"
    print("Data selection test (Competitions) passed.")


def test_update_data_competitions():
    query = """
    UPDATE competitions
    SET competition_name = 'MedGen World Championship'
    WHERE competition_name = 'MedGen Challenge';
    """
    response = execute_sql_query(query)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert response.json().get("message") == "Query executed successfully", "Update failed"
    print("Data update test (Competitions) passed.")


def test_delete_data_competitions():
    query = """
    DELETE FROM competitions WHERE competition_name = 'MedGen World Championship';
    """
    response = execute_sql_query(query)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert response.json().get("message") == "Query executed successfully", "Delete failed"
    print("Data deletion test (Competitions) passed.")


if __name__ == "__main__":
    run_tests()
