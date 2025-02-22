# services/admin.py

from __init__ import db
from models import *
from sqlalchemy import text, bindparam, func
from datetime import datetime 
import os
from flask import jsonify, flash
from werkzeug.utils import secure_filename
from decimal import Decimal

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

def get_guesses_per_month():
    try:
        query = text("""
SELECT 
    TO_CHAR(date_of_guess, 'YYYY-MM') AS month,
    COUNT(*) AS guess_count
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
                COUNT(img.image_id) AS totalReal,
                COALESCE(
                    SUM(CASE WHEN ug.user_guess_type = 'real' THEN 1 ELSE 0 END) * 1.0 / COUNT(ug.guess_id), 
                    0
                ) AS percentageDetected
            FROM images img
            LEFT JOIN user_guesses ug ON ug.image_id = img.image_id
            LEFT JOIN feedback_users fu ON fu.guess_id = ug.guess_id
            WHERE img.image_type = 'real';
        """)
        result = db.session.execute(query)
        db.session.commit()

        row = result.fetchone()
        if row:
            return {
                "totalReal": int(row[0]),
                "percentageDetected": float(row[1]) if isinstance(row[1], Decimal) else 0.0  # Convert Decimal to float
            }
        return {}
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}

def get_total_ai_images():
    try:
        query = text("""
            SELECT 
                COUNT(img.image_id) AS totalAI,
                COALESCE(
                    SUM(CASE WHEN ug.user_guess_type = 'ai' THEN 1 ELSE 0 END) * 1.0 / COUNT(ug.guess_id), 
                    0
                ) AS percentageDetected
            FROM images img
            LEFT JOIN user_guesses ug ON ug.image_id = img.image_id
            LEFT JOIN feedback_users fu ON fu.guess_id = ug.guess_id
            WHERE img.image_type = 'ai';
        """)
        result = db.session.execute(query)
        db.session.commit()

        row = result.fetchone()
        if row:
            return {
                "totalAI": int(row[0]),  
                "percentageDetected": float(row[1]) if isinstance(row[1], Decimal) else 0.0
            }
        return {}
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}

def get_feedback_resolution_status():
    try:
        query = text("""
            SELECT 
                SUM(CASE WHEN resolved IS TRUE THEN 1 ELSE 0 END) AS resolvedCount,
                SUM(CASE WHEN resolved IS FALSE THEN 1 ELSE 0 END) AS unresolvedCount
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



    







UPLOAD_FOLDER = '../MedGenAI-Images/Images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image_service(request, image_type):
    """
    Handles file upload and saves the record in the database using execute() for SQL insertion.
    
    :param request: Flask request object containing the file
    :param image_type: 'real' or 'ai' (used for categorization)
    """
    if 'file' not in request.files:
        flash('No file part')
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        if image_type == 'real':
            folder = 'real-images-upload'
        elif image_type == 'ai':
            folder = 'ai-images-upload'
        else:
            return jsonify({'error': 'Invalid image type'}), 400

        filepath = os.path.join(UPLOAD_FOLDER, folder, filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        file.save(filepath)

        query = text("""
            INSERT INTO images (image_path, image_type, upload_time)
            VALUES (:image_path, :image_type, :upload_time)
            RETURNING image_id
        """)

        params = {
            'image_path': "/" + os.path.join(folder, filename),
            'image_type': image_type,
            'upload_time': datetime.utcnow()
        }

        try:
            result = db.session.execute(query, params)
            db.session.commit()

            new_image_id = result.scalar()  

            flash(f'{image_type.capitalize()} image successfully uploaded')
            return jsonify({
                'message': f'{image_type.capitalize()} image uploaded successfully',
                'image_id': new_image_id,
                'filepath': filepath
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    flash('Invalid file format')
    return jsonify({'error': 'Invalid file format'}), 400




def filter_users_by_tags(tag_names, match_all=True, sort_by="level", desc=True):
    """
    Filters users based on tags, either matching ANY tag or ALL tags.

    :param tag_names: List of tag names to filter users by.
    :param match_all: If True, returns users with ALL tags. 
                      If False, returns users with ANY tag.
    :return: List of user objects.
    """
    tag_names = [t.lower() for t in tag_names]
    query = db.session.query(
    		Users,
    		func.count(func.distinct(UserGuess.guess_id)).label("total_guesses"),
    		func.count(func.distinct(UserGuess.guess_id)).filter(UserGuess.user_guess_type == Images.image_type).label("correct_guesses")
    ).join(UserTags).join(Tag).filter(func.lower(Tag.name).in_(tag_names)) \
     .join(UserGuess, UserGuess.user_id == Users.user_id, isouter = True) \
     .join(Images, Images.image_id == UserGuess.image_id, isouter = True) \
     .group_by(Users.user_id)

    if match_all:
        query = query.having(func.count(func.distinct(Tag.tag_id)) >= len(tag_names))
    else:
        query = query.distinct()

    data = [{
    	"username": user.username, 
    	"level": user.level, 
    	"games_started": user.games_started, 
    	"score": user.score, 
    	"accuracy": round((correct_guesses / total_guesses * 100) if total_guesses else 0, 2), 
    	"engagement": total_guesses
    	} for user, total_guesses, correct_guesses in query.all()]
    	
    return sorted(data, key = lambda x: x[sort_by], reverse = desc)
