# services/admin.py

from __init__ import db
from sqlalchemy import text

# Function to get guesses per month
def get_guesses_per_month():
    try:
        query = text("""
            SELECT 
                strftime('%Y-%m', date_of_guess) AS month,
                COUNT(*) AS guessCount
            FROM user_guesses
            WHERE date_of_guess >= date('now', '-12 months')
            GROUP BY month
            ORDER BY month;
        """)
        result = db.session.execute(query)
        db.session.commit()

        # Convert query result to a list of dictionaries
        rows = []
        for row in result:
            row_dict = {column: value for column, value in zip(result.keys(), row)}
            rows.append(row_dict)

        return rows
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}

# Function to get image detection accuracy per month
def get_image_detection_accuracy():
    try:
        query = text("""
            SELECT 
                strftime('%Y-%m', date_of_guess) AS month,
                SUM(CASE WHEN user_guess_type = (SELECT image_type FROM images WHERE images.image_id = user_guesses.image_id) THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS accuracy
            FROM user_guesses
            WHERE date_of_guess >= date('now', '-12 months')
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

# Function to get feedback instances per month
def get_feedback_instances():
    try:
        query = text("""
            SELECT 
                strftime('%Y-%m', (SELECT date_of_guess FROM user_guesses WHERE user_guesses.guess_id = feedback_users.guess_id)) AS month,
                COUNT(*) AS feedbackCount
            FROM feedback_users
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

# Function to get total real images and detection accuracy
def get_total_real_images():
    try:
        query = text("""
            SELECT 
                COUNT(*) AS totalReal,
                SUM(CASE WHEN (SELECT user_guess_type FROM user_guesses WHERE user_guesses.image_id = images.image_id) = 'real' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS percentageDetected
            FROM images
            WHERE image_type = 'real';
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

# Function to get total AI images and detection accuracy
def get_total_ai_images():
    try:
        query = text("""
            SELECT 
                COUNT(*) AS totalAI,
                SUM(CASE WHEN (SELECT user_guess_type FROM user_guesses WHERE user_guesses.image_id = images.image_id) = 'ai' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS percentageDetected
            FROM images
            WHERE image_type = 'ai';
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

# Function to get feedback resolution status (resolved and unresolved counts)
def get_feedback_resolution_status():
    try:
        query = text("""
            SELECT 
                SUM(CASE WHEN resolved = 1 THEN 1 ELSE 0 END) AS resolvedCount,
                SUM(CASE WHEN resolved = 0 THEN 1 ELSE 0 END) AS unresolvedCount
            FROM feedback;
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

# Function to get matching feedback for a specific image
def get_matching_feedback_for_image(image_id):
    try:
        query = text(f"""
            SELECT 
                feedback_users.guess_id, 
                feedback_users.msg, 
                feedback_users.x AS x, 
                feedback_users.y AS y
            FROM feedback_users
            JOIN user_guesses ON feedback_users.guess_id = user_guesses.guess_id
            JOIN images ON user_guesses.image_id = images.image_path
            WHERE user_guesses.image_id = '{image_id}'
            AND user_guesses.user_guess_type = images.image_type;
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

# Function to get random unresolved feedback for a specific image
def get_random_unresolved_feedback(image_id):
    try:
        query = text(f"""
            SELECT feedback_users.guess_id, feedback_users.feedback_message
            FROM feedback_users
            JOIN user_guesses ON feedback_users.guess_id = user_guesses.guess_id
            JOIN feedback ON feedback_users.guess_id = feedback.feedback_id
            WHERE user_guesses.image_id = '{image_id}'
            AND feedback.resolved = 0
            ORDER BY RANDOM()
            LIMIT 1;
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
