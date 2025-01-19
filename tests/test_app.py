import sys
import os
import pytest
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app, db, Competition, CompetitionUser


@pytest.fixture
def client():
    # in-memory sqlite db so we dont need to worry about affecting the main one
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    with app.app_context():
        db.create_all() 
        yield app.test_client()
        db.drop_all()  # Drop the tables after the test

# Test for creating a competition using raw SQL through execute_sql route
def test_create_competition(client):
    sql_query = """
    INSERT INTO competitions (name, start_date, end_date) 
    VALUES ('Competition 1', '2025-01-01 00:00:00', '2025-02-01 00:00:00')
    """

    response = client.post('/execute_sql', json={'query': sql_query})

    print("Response Status Code:", response.status_code)
    print("Response Body:", response.json)

    assert response.status_code == 200
    assert 'Query executed successfully' in response.json.get('message')

    competition = db.session.execute(text('SELECT * FROM competitions WHERE name = "Competition 1"')).fetchone()

    assert competition is not None
    assert competition[1] == 'Competition 1'
    assert competition[2] == '2025-01-01 00:00:00'
    assert competition[3] == '2025-02-01 00:00:00'


# Test for getting all competitions using raw SQL through execute_sql route
def test_get_competitions(client):
    sql_query = """
    INSERT INTO competitions (name, start_date, end_date) 
    VALUES ('Test Competition', '2025-01-01 00:00:00', '2025-02-01 00:00:00')
    """
    client.post('/execute_sql', json={'query': sql_query})

    sql_query = 'SELECT * FROM competitions'
    response = client.post('/execute_sql', json={'query': sql_query})

    print("Response Status Code:", response.status_code)
    print("Response Body:", response.json)

    assert response.status_code == 200
    data = response.json
    assert len(data) > 0
    assert data[0]["name"] == 'Test Competition'


def test_create_competition_user(client):

    sql_query = """
    INSERT INTO competitions (name, start_date, end_date) 
    VALUES ('Test Competition', '2025-01-01 00:00:00', '2025-02-01 00:00:00')
    """
    client.post('/execute_sql', json={'query': sql_query})

    competition_id = db.session.execute(text('SELECT id FROM competitions WHERE name = "Test Competition"')).fetchone()[0]

    sql_query = f"""
    INSERT INTO competition_users (competition_id, user_id, score) 
    VALUES ({competition_id}, 1, 100)
    """
    response = client.post('/execute_sql', json={'query': sql_query})

    print("Response Status Code:", response.status_code)
    print("Response Body:", response.json)

    assert response.status_code == 200
    assert 'Query executed successfully' in response.json.get('message')

    user = db.session.execute(text(f'SELECT * FROM competition_users WHERE competition_id = {competition_id}')).fetchone()

    # Assert the competition user was created successfully
    assert user is not None
    assert user[1] == competition_id
    assert user[2] == 1
    assert user[3] == 100


def test_get_competition_users(client):
    sql_query = """
    INSERT INTO competitions (name, start_date, end_date) 
    VALUES ('Test Competition', '2025-01-01 00:00:00', '2025-02-01 00:00:00')
    """
    client.post('/execute_sql', json={'query': sql_query})

    competition_id = db.session.execute(text('SELECT id FROM competitions WHERE name = "Test Competition"')).fetchone()[0]

    sql_query = f"""
    INSERT INTO competition_users (competition_id, user_id, score) 
    VALUES ({competition_id}, 1, 50)
    """
    client.post('/execute_sql', json={'query': sql_query})

    sql_query = 'SELECT * FROM competition_users'
    response = client.post('/execute_sql', json={'query': sql_query})

    print("Response Status Code:", response.status_code)
    print("Response Body:", response.json)


    assert response.status_code == 200
    data = response.json
    assert len(data) > 0
    data = data[0]
    assert data["competition_id"] == competition_id
    assert data["id"] == 1
    assert data["score"] == 50 
    assert data["user_id"] == 1 

# Test for invalid route
def test_invalid_route(client):
    response = client.get('/invalid_route')
    assert response.status_code == 404
