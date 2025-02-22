from __init__ import db
from models import *
from sqlalchemy import text



def get_image_detection_accuracy():
    try:
        query = text("""
SELECT 
    TO_CHAR(date_of_guess, 'YYYY-MM') AS month,
    SUM(CASE WHEN user_guess_type = (SELECT image_type FROM images WHERE images.image_id = user_guesses.image_id) THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS accuracy
FROM user_guesses
WHERE date_of_guess >= NOW() - INTERVAL '12 months'
GROUP BY month
ORDER BY month;
        """)
        result = db.session.execute(query)
        db.session.commit()

        rows = []
        for row in result:
            row_dict = {column: value for column, value in zip(result.keys(), row)}
            rows.append(row_dict)

        return rows
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}


def get_confusion_matrix():
    try:
        query = text("""
            SELECT
                SUM(CASE WHEN user_guess_type = 'real' AND image_type = 'real' THEN 1 ELSE 0 END) AS truePositive,
                SUM(CASE WHEN user_guess_type = 'ai' AND image_type = 'real' THEN 1 ELSE 0 END) AS falsePositive,
                SUM(CASE WHEN user_guess_type = 'real' AND image_type = 'ai' THEN 1 ELSE 0 END) AS falseNegative,
                SUM(CASE WHEN user_guess_type = 'ai' AND image_type = 'ai' THEN 1 ELSE 0 END) AS trueNegative
            FROM user_guesses
            JOIN images ON user_guesses.image_id = images.image_id;
        """)
        result = db.session.execute(query)
        db.session.commit()

        confusion_matrix = {}
        for row in result:
            confusion_matrix = {column: value for column, value in zip(result.keys(), row)}

        return confusion_matrix
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}



def get_ml_metrics():
    try:
        # Use text() to ensure that SQLAlchemy knows it's a raw SQL query
        query = text("""
            SELECT 
                SUM(CASE WHEN user_guesses.user_guess_type = images.image_type AND user_guesses.user_guess_type = 'real' THEN 1 ELSE 0 END) AS true_positive,
                SUM(CASE WHEN user_guesses.user_guess_type != images.image_type AND user_guesses.user_guess_type = 'real' THEN 1 ELSE 0 END) AS false_positive,
                SUM(CASE WHEN user_guesses.user_guess_type = images.image_type AND user_guesses.user_guess_type = 'ai' THEN 1 ELSE 0 END) AS true_negative,
                SUM(CASE WHEN user_guesses.user_guess_type != images.image_type AND user_guesses.user_guess_type = 'ai' THEN 1 ELSE 0 END) AS false_negative
            FROM user_guesses
            JOIN images ON user_guesses.image_id = images.image_id
        """)

        # Execute the query and commit the transaction
        result = db.session.execute(query)
        db.session.commit()

        # Get the results as a dictionary
        row = result.fetchone()
        if not row:
            return {"error": "No data found"}

        true_positive = row[0]
        false_positive = row[1]
        true_negative = row[2]
        false_negative = row[3]

        # Calculate the metrics
        accuracy = (true_positive + true_negative) / (true_positive + false_positive + true_negative + false_negative)
        precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) != 0 else 0
        recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) != 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1Score": f1_score
        }

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}


def get_leaderboard():
    try:
        query = text("""
SELECT 
    user_guesses.user_id, 
    username,
    AVG(CASE WHEN user_guess_type = image_type THEN 1 ELSE 0 END) AS accuracy
FROM user_guesses
JOIN images ON user_guesses.image_id = images.image_id
JOIN users ON users.user_id = user_guesses.user_id
GROUP BY user_guesses.user_id, users.username
ORDER BY accuracy DESC
LIMIT 10;
        """)
        result = db.session.execute(query)
        db.session.commit()

        leaderboard = []
        for row in result:
            leaderboard.append({column: value for column, value in zip(result.keys(), row)})

        return leaderboard
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}


def get_image_difficulty():
    try:
        query = text("""
            SELECT 
                images.image_id, 
                images.image_path,
                COUNT(*) AS total_guesses,
                SUM(CASE WHEN user_guess_type != images.image_type THEN 1 ELSE 0 END) AS incorrect_guesses,
                (SUM(CASE WHEN user_guess_type != images.image_type THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) AS difficulty_score
            FROM user_guesses
            JOIN images ON user_guesses.image_id = images.image_id
            GROUP BY images.image_id
            ORDER BY difficulty_score DESC;
        """)
        result = db.session.execute(query)
        db.session.commit()

        difficulty_data = []
        for row in result:
            difficulty_data.append({column: value for column, value in zip(result.keys(), row)})

        return difficulty_data
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}





