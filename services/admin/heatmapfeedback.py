# services/admin.py

from __init__ import db
from models import *
from sqlalchemy import text


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
    





    
def get_image_confusion_matrix(image_id):
    try:
        query = text(f"""
            SELECT
                SUM(CASE WHEN user_guesses.user_guess_type = 'real' AND images.image_type = 'real' THEN 1 ELSE 0 END) AS truePositive,
                SUM(CASE WHEN user_guesses.user_guess_type = 'ai' AND images.image_type = 'real' THEN 1 ELSE 0 END) AS falsePositive,
                SUM(CASE WHEN user_guesses.user_guess_type = 'real' AND images.image_type = 'ai' THEN 1 ELSE 0 END) AS falseNegative,
                SUM(CASE WHEN user_guesses.user_guess_type = 'ai' AND images.image_type = 'ai' THEN 1 ELSE 0 END) AS trueNegative
            FROM user_guesses
            JOIN images ON user_guesses.image_id = images.image_id
            WHERE images.image_id = {image_id}
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








