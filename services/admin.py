# services/admin.py

from __init__ import db
from sqlalchemy import text, bindparam
from datetime import datetime 

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

        rows = []
        for row in result:
            row_dict = {column: value for column, value in zip(result.keys(), row)}
            rows.append(row_dict)

        return rows
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}

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

def get_leaderboard():
    try:
        query = text("""
            SELECT 
                user_guesses.user_id, 
                username,
                AVG(CASE WHEN user_guess_type = image_type THEN 1 ELSE 0 END) AS accuracy
            FROM user_guesses
            JOIN images ON user_guesses.image_id = images.image_id
            JOIN users on users.user_id = user_guesses.user_id
            GROUP BY user_guesses.user_id
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

def get_feedback_resolution_status():
    try:
        query = text("""
            SELECT 
                SUM(CASE WHEN resolved IS TRUE THEN 1 ELSE 0 END) AS resolvedCount,
                SUM(CASE WHEN resolved IS TRUE THEN 1 ELSE 0 END) AS unresolvedCount
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

def get_matching_feedback_for_image(image_id):
    try:
        query = text(f"""
            SELECT 
                feedback.feedback_id, 
                feedback.msg, 
                feedback.x AS x, 
                feedback.y AS y
            FROM feedback
            JOIN feedback_users ON feedback_users.feedback_id = feedback.feedback_id
            JOIN user_guesses ON feedback_users.guess_id = user_guesses.guess_id
            JOIN images ON user_guesses.image_id = images.image_id
            WHERE user_guesses.image_id = {image_id}
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

def get_random_unresolved_feedback(image_id):
    try:
        query = text(f"""
            SELECT feedback_users.guess_id, feedback_users.feedback_message
            FROM feedback_users
            JOIN user_guesses ON feedback_users.guess_id = user_guesses.guess_id
            JOIN feedback ON feedback_users.guess_id = feedback.feedback_id
            WHERE user_guesses.image_id = '{image_id}'
            AND feedback.resolved IS FALSE
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



def get_feedback_with_filters(image_type=None, resolved=None, sort_by=None):
    try:
        query_str = """
            SELECT 
                images.image_id,
                images.image_path,
                images.image_type,
                COUNT(CASE WHEN feedback.resolved IS FALSE THEN 1 END) AS unresolved_count,
                MAX(feedback.date_added) AS last_feedback_time,
                images.upload_time
            FROM images
            LEFT JOIN user_guesses ON user_guesses.image_id = images.image_id
            LEFT JOIN feedback_users ON feedback_users.guess_id = user_guesses.guess_id
            LEFT JOIN feedback ON feedback.feedback_id = feedback_users.feedback_id
            WHERE 1=1
        """

        if image_type != "all":
            query_str += " AND images.image_type = :image_type"

        if resolved is not None:
            query_str += " AND feedback.resolved IS :resolved"

        if sort_by:
            valid_sort_fields = ['last_feedback_time', 'unresolved_count', 'upload_time']
            if sort_by == "image_id":
                query_str += "ORDER BY images.image_id"  # Resolves ambiguous image_id reference
            elif sort_by in valid_sort_fields:
                query_str += f" ORDER BY {sort_by}"
            else:
                raise ValueError("Invalid sort field provided.")

        query = text(query_str)

        params = {}
        if image_type:
            params['image_type'] = image_type
        if resolved is not None:
            params['resolved'] = resolved

        result = db.session.execute(query, params)

        feedback_data = []
        for row in result.mappings(): 
            last_feedback_time = row['last_feedback_time']
            if isinstance(last_feedback_time, str):
                last_feedback_time = last_feedback_time 
            elif isinstance(last_feedback_time, datetime): 
                last_feedback_time = last_feedback_time.strftime('%Y-%m-%d')
            else:
                last_feedback_time = None

            upload_time = row['upload_time']
            if isinstance(upload_time, str):
                upload_time = upload_time 
            elif isinstance(upload_time, datetime):
                upload_time = upload_time.strftime('%Y-%m-%d')
            else:
                upload_time = None

            feedback_data.append({
                'image_id': row['image_id'],
                'image_path': row['image_path'],
                'image_type': row['image_type'],
                'unresolved_count': row['unresolved_count'],
                'last_feedback_time': last_feedback_time,
                'upload_time': upload_time
            })

        return feedback_data 
    except Exception as e:
        print(f"Error fetching feedback: {e}")
        return []
    

def get_image_by_id(image_id):
    try:
        query = text("""
            SELECT 
                image_id, 
                image_path, 
                image_type, 
                upload_time 
            FROM images 
            WHERE image_id = :image_id
        """)
        result = db.session.execute(query, {"image_id": image_id})
        db.session.commit()

        row = result.fetchone()
        
        if row:
            image_data = {column: value for column, value in zip(result.keys(), row)}
            return image_data
        else:
            return None

    except Exception as e:
        db.session.rollback()
        print(f"Error fetching image by id: {e}")
        return None

def fetch_data_for_csv(table_name):
    try:
        query = text(f"SELECT * FROM {table_name}")
        
        result = db.session.execute(query)
        db.session.commit()

        columns = result.keys()

        rows = result.fetchall()

        data = [dict(zip(columns, row)) for row in rows]

        return data

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error fetching data for table {table_name}: {e}")

def get_metadata_counts():
    try:
        queries = {
            'feedback': "SELECT COUNT(*) FROM feedback_users",
            'image': "SELECT COUNT(*) FROM images",
            'leaderboard': "SELECT COUNT(*) FROM user_guesses",
            'competition': "SELECT COUNT(*) FROM competitions" 
        }

        counts = {}


        for table, query in queries.items():
            result = db.session.execute(text(query))
            db.session.commit()
            count = result.fetchone()[0]
            counts[table] = count

        return counts

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}