# services/admin.py

from __init__ import db
from models import *
from sqlalchemy import text
from datetime import datetime 



def get_feedback_with_filters(image_type=None, resolved=None, sort_by=None, sort_order='asc', limit=20, offset=0):
    try:
        # Start the query string
        query_str = """
            SELECT 
                images.image_id,
                images.image_path,
                images.image_type,
                COUNT(CASE WHEN feedback.resolved IS false THEN 1 END) AS unresolved_count,
                MAX(feedback.date_added) AS last_feedback_time,
                images.upload_time
            FROM images
            LEFT JOIN user_guesses ON user_guesses.image_id = images.image_id
            LEFT JOIN feedback_users ON feedback_users.guess_id = user_guesses.guess_id
            LEFT JOIN feedback ON feedback.feedback_id = feedback_users.feedback_id

            WHERE 1=1
        """

        # Apply filters for image_type if provided
        if image_type and image_type != "all":
            query_str += " AND images.image_type = :image_type"

        query_str += """
            GROUP BY images.image_id, images.image_path, images.image_type, images.upload_time
        """

        # Apply HAVING clause if resolved is False
        if resolved is False:
            query_str += """
                HAVING COUNT(CASE WHEN feedback.resolved IS false THEN 1 END) > 0
            """
        if resolved:
            query_str += """
                HAVING COUNT(CASE WHEN feedback.resolved IS false THEN 1 END) = 0
"""

        # Apply sorting based on sort_by field
        valid_sort_fields = ['last_feedback_time', 'unresolved_count', 'upload_time']
        if sort_by:
            if sort_by in valid_sort_fields:
                query_str += f" ORDER BY {sort_by} {sort_order.upper()}"
            elif sort_by == "image_id":
                query_str += f" ORDER BY images.image_id {sort_order.upper()}"
            else:
                raise ValueError("Invalid sort field provided.")
        else:
            query_str += f" ORDER BY last_feedback_time {sort_order.upper()}"

        # Add LIMIT and OFFSET for pagination
        query_str += f" LIMIT :limit OFFSET :offset"

        # Prepare parameters for query execution
        params = {
            'limit': limit,
            'offset': offset
        }

        # If image_type filter is provided, add to params
        if image_type:
            params['image_type'] = image_type
        if resolved is not None:
            params['resolved'] = resolved

        # Execute the query
        query = text(query_str)
        result = db.session.execute(query, params)

        # Process and format the results
        feedback_data = []
        for row in result.mappings():
            feedback_data.append({
                'image_id': row['image_id'],
                'image_path': row['image_path'],
                'image_type': row['image_type'],
                'unresolved_count': row['unresolved_count'],
                'last_feedback_time': (
                    row['last_feedback_time'].strftime('%Y-%m-%d')
                    if isinstance(row['last_feedback_time'], datetime) else row['last_feedback_time']
                ),
                'upload_time': (
                    row['upload_time'].strftime('%Y-%m-%d')
                    if isinstance(row['upload_time'], datetime) else row['upload_time']
                ),
            })

        return feedback_data

    except Exception as e:
        print(f"Error fetching feedback: {e}")
        return []
    


def get_feedback_count(image_type=None, resolved=None):
    try:
        count_query_str = """
            SELECT COUNT(DISTINCT images.image_id) 
            FROM images
            LEFT JOIN user_guesses ON user_guesses.image_id = images.image_id
            LEFT JOIN feedback_users ON feedback_users.guess_id = user_guesses.guess_id
            LEFT JOIN feedback ON feedback.feedback_id = feedback_users.feedback_id
            WHERE 1=1
        """

        if image_type and image_type != "all":
            count_query_str += " AND images.image_type = :image_type"

        if resolved is not None:
            count_query_str += f" AND feedback.resolved IS {'true' if resolved else 'false'}"

        count_query = text(count_query_str)
        params = {
            'image_type': image_type,
            'resolved': resolved
        }
        count_result = db.session.execute(count_query, params)

        total_count = count_result.scalar()

        return total_count

    except Exception as e:
        print(f"Error fetching feedback count: {e}")
        return 0



def resolve_all_feedback_by_image(image_id: int):
    try:
        query = text("""
            SELECT ug.guess_id
            FROM user_guesses ug
            JOIN images img ON ug.image_id = img.image_id
            WHERE img.image_id = :image_id
        """)
        result = db.session.execute(query, {'image_id': image_id})
        db.session.commit()

        guess_ids = [row[0] for row in result]

        if not guess_ids:
            return {"error": "No guesses found for the given image_id"}

        update_query = text("""
            UPDATE feedback
            SET resolved = TRUE
            WHERE feedback_id IN (
                SELECT fu.feedback_id
                FROM feedback_users fu
                JOIN feedback f ON fu.feedback_id = f.feedback_id
                WHERE fu.guess_id IN :guess_ids
            )
        """)
        db.session.execute(update_query, {'guess_ids': tuple(guess_ids)})
        db.session.commit()

        return {"message": "All feedback for the image has been marked as resolved"}

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}






