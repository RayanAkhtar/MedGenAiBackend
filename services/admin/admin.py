from __init__ import db
from models import Users, Admin, UserGuess, Images, FeedbackUser, Feedback, Competition, Tag, UserTags
from sqlalchemy import func, desc, text, case, and_
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import os
import logging
from flask import jsonify, flash
from werkzeug.utils import secure_filename
from decimal import Decimal

def get_metadata_counts():
    try:
        counts = {
            'feedback': db.session.query(func.count(FeedbackUser.guess_id)).scalar(),
            'image': db.session.query(func.count(Images.image_id)).scalar(),
            'leaderboard': db.session.query(func.count(UserGuess.guess_id)).scalar(),
            'competition': db.session.query(func.count(Competition.competition_id)).scalar()
        }
        return counts
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}

def get_guesses_per_month():
    try:
        result = db.session.query(
            func.to_char(UserGuess.date_of_guess, 'YYYY-MM').label("month"),
            func.count().label("guess_count")
        ).filter(
            UserGuess.date_of_guess >= func.now() - text("INTERVAL '12 months'")
        ).group_by("month").order_by("month").all()

        return [{"month": row.month, "guess_count": row.guess_count} for row in result]
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}

def get_feedback_instances():
    try:
        result = db.session.query(
            func.to_char(UserGuess.date_of_guess, 'YYYY-MM').label("month"),
            func.count().label("feedbackCount")
        ).join(FeedbackUser, FeedbackUser.guess_id == UserGuess.guess_id
               ).group_by("month").order_by("month").all()

        return [{"month": row.month, "feedbackCount": row.feedbackCount} for row in result]
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}

def get_total_real_images():
    try:
        result = db.session.query(
            func.count(Images.image_id).label("totalReal"),
            func.coalesce(
                func.sum(
                    case(
                        (UserGuess.user_guess_type == 'real', 1), 
                        else_=0
                    )
                ) * 1.0 / func.nullif(func.count(UserGuess.guess_id), 0),
                0
            ).label("percentageDetected")
        ).outerjoin(UserGuess, UserGuess.image_id == Images.image_id
                    ).filter(Images.image_type == 'real').first()

        return {"totalReal": result.totalReal, "percentageDetected": float(result.percentageDetected)} if result else {}
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}



def get_total_ai_images():
    try:
        result = db.session.query(
            func.count(Images.image_id).label("totalAI"),
            func.coalesce(
                func.sum(
                    case(
                        (UserGuess.user_guess_type == 'ai', 1), 
                        else_=0
                    )
                ) * 1.0 / func.nullif(func.count(UserGuess.guess_id), 0),
                0
            ).label("percentageDetected")
        ).outerjoin(UserGuess, UserGuess.image_id == Images.image_id
                    ).filter(Images.image_type == 'ai').first()

        return {"totalAI": result.totalAI, "percentageDetected": float(result.percentageDetected)} if result else {}
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}




def get_feedback_resolution_status():
    try:
        result = db.session.query(
            func.sum(case((Feedback.resolved == True, 1), else_=0)).label("resolvedCount"),
            func.sum(case((Feedback.resolved == False, 1), else_=0)).label("unresolvedCount")
        ).first()

        return {"resolvedCount": result.resolvedCount, "unresolvedCount": result.unresolvedCount} if result else {}
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}

def get_random_unresolved_feedback(image_id):
    try:
        result = db.session.query(FeedbackUser.guess_id, FeedbackUser.feedback_message
            ).join(UserGuess, FeedbackUser.guess_id == UserGuess.guess_id
            ).join(Feedback, FeedbackUser.guess_id == Feedback.feedback_id
            ).filter(UserGuess.image_id == image_id, Feedback.resolved.is_(False)
            ).order_by(func.random()).limit(1).all()

        return [{"guess_id": row.guess_id, "feedback_message": row.feedback_message} for row in result]
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}

def list_tags(admin_id, admin_only=False):
    try:
        if admin_only:
            tags = db.session.query(Tag.name).filter(Tag.admin_id == admin_id).distinct().all()
        else:
            tags = db.session.query(Tag.name).filter(
                (Tag.admin_id == admin_id) | (Tag.admin_id == None)
            ).distinct().all()
        return [tag[0] for tag in tags]
    except Exception as e:
        logging.error(f"Error fetching tags: {str(e)}", exc_info=True)
        raise

def filter_users_by_tags(tag_names, match_all=True):
    try:
        query = None
        
        if not tag_names or len(tag_names) == 0:
            # Return all users
            query = db.session.query(
                Users,
                func.count(func.distinct(UserGuess.guess_id)).label("total_guesses"),
                func.count(func.distinct(UserGuess.guess_id)).filter(UserGuess.user_guess_type == Images.image_type).label("correct_guesses")
            ).outerjoin(UserGuess, UserGuess.user_id == Users.user_id
            ).outerjoin(Images, Images.image_id == UserGuess.image_id
            ).outerjoin(Admin, Admin.user_id == Users.user_id
            ).filter(Admin.user_id.is_(None)
            ).group_by(Users.user_id)
        else:
            tag_names = [t.lower() for t in tag_names]    
            # Base query
            query = db.session.query(
                Users,
                func.count(func.distinct(UserGuess.guess_id)).label("total_guesses"),
                func.count(func.distinct(UserGuess.guess_id)).filter(UserGuess.user_guess_type == Images.image_type).label("correct_guesses")
            ).join(UserTags).join(Tag).filter(func.lower(Tag.name).in_(tag_names)
            ).outerjoin(UserGuess, UserGuess.user_id == Users.user_id
            ).outerjoin(Images, Images.image_id == UserGuess.image_id
            ).group_by(Users.user_id)

            # Apply filter for tags
            if match_all:
                query = query.having(func.count(func.distinct(Tag.tag_id)) >= len(tag_names))
        return query
        
    except Exception as e:
        logging.error(f"Error in filter_users_by_tags: {str(e)}", exc_info=True)
        raise


def paginated_filter_users_by_tags(tag_names, match_all=True, sort_by="username", desc=True, limit=10, offset=0):
    try:
        query = filter_users_by_tags(tag_names, match_all)
        sort_column = getattr(Users, sort_by) if sort_by in ["username", "level", "score", "games_started"] else None
        
        # Sorting
        if sort_column:
            query = query.order_by(sort_column.desc() if desc else sort_column)
        
        # Pagination
        query = query.limit(limit).offset(offset)

        # Fetch results
        data = [{
            "username": user.username,
            "level": user.level,
            "games_started": user.games_started,
            "score": user.score,
            "accuracy": round((correct_guesses / total_guesses * 100) if total_guesses else 0, 2),
            "engagement": total_guesses
        } for user, total_guesses, correct_guesses in query.all()]

        if sort_by in ["accuracy", "engagement"]:
            data = sorted(data, key=lambda x: x[sort_by], reverse=desc)
        return data
        
    except Exception as e:
        logging.error(f"Error in paginated_filter_users_by_tags: {str(e)}", exc_info=True)
        raise

def count_users_by_tags(tag_names, match_all=True):
    try:
        query = None
        if not tag_names or len(tag_names) == 0:
            query = db.session.query(Users.user_id
            ).outerjoin(Admin, Admin.user_id == Users.user_id
            ).filter(Admin.user_id.is_(None))
        else:
            tag_names = [t.lower() for t in tag_names]

            # Base query
            query = db.session.query(
                Users.user_id
            ).join(UserTags).join(Tag
            ).outerjoin(Admin, Admin.user_id == Users.user_id
            ).filter(
                func.lower(Tag.name).in_(tag_names),
                Admin.user_id.is_(None) 
            ).group_by(Users.user_id)

            # Apply filter for tags
            if match_all:
                query = query.having(func.count(func.distinct(Tag.tag_id)) >= len(tag_names))

        count = query.count()
        return count if count is not None else 0
    except Exception as e:
        logging.error(f"Error in count_users_by_tags: {str(e)}", exc_info=True)
        raise

def assign_tags_to_users(usernames, tags, admin_id, select_all=False, filter_tags=[], match_all=False):
    try:
        tag_results = db.session.query(Tag).filter(
            and_(
                Tag.name.in_(tags),
                Tag.admin_id == admin_id
            )
        ).all()

        if not tag_results:
            return jsonify({"error": "No valid private tags found for the provided admin ID."}), 400
        
        tag_id_map = {tag.name: tag.tag_id for tag in tag_results}

        if select_all:
            query = filter_users_by_tags(filter_tags, match_all)
            if not query:
                return jsonify({"error": "No users found matching filters"}), 400
            all_users = query.with_entities(Users.user_id).all()
            all_user_ids = {user.user_id for user in all_users}
            
            excluded_users = db.session.query(Users.user_id).filter(Users.username.in_(usernames)).all()
            excluded_user_ids = {user.user_id for user in excluded_users}
            user_ids = all_user_ids - excluded_user_ids
        else:
            users = db.session.query(Users).filter(Users.username.in_(usernames)).all()
            if not users:
                return jsonify({"error": "No valid users found for the provided usernames."}), 400
            user_ids = {user.user_id for user in users}

        if not user_ids:
            return jsonify({"message": "No users to assign tags to."}), 200
                
        new_user_tags = []
        existing_user_tags = db.session.query(UserTags).filter(
            UserTags.user_id.in_(user_ids),
            UserTags.tag_id.in_(tag_id_map.values())
        ).all()

        existing_user_tag_set = {(ut.user_id, ut.tag_id) for ut in existing_user_tags}

        for user_id in user_ids:
            for tag_name in tags:
                if tag_name in tag_id_map:
                    tag_id = tag_id_map[tag_name]
                    if (user_id, tag_id) not in existing_user_tag_set:
                        new_user_tags.append(UserTags(user_id=user_id, tag_id=tag_id))
                        
        if new_user_tags:
            db.session.bulk_save_objects(new_user_tags)
            db.session.commit()
            return jsonify({"message": f"Tags assigned successfully to {len(user_ids)} users."}), 200
            
        return jsonify({"message": "No new tags to assign."}), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error assigning tags to users: {e}")
        return jsonify({"error": "An error occurred while assigning tags."}), 500

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

    sex = request.form.get('sex')
    age = request.form.get('age', type=int)
    disease = request.form.get('disease')

    if sex not in ['Male', 'Female']:
        return jsonify({'error': 'Invalid sex value'}), 400
    if age is None or not (18 <= age <= 100):
        return jsonify({'error': 'Invalid age value'}), 400
    if disease not in ['None', 'Pleural_Effusion']:
        return jsonify({'error': 'Invalid disease value'}), 400
    if disease == 'None':
        disease = 'none'
         
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
            INSERT INTO images (image_path, image_type, upload_time, gender, age, disease)
            VALUES (:image_path, :image_type, :upload_time, :gender, :age, :disease)
            RETURNING image_id
        """)

        params = {
            'image_path': "/" + os.path.join(folder, filename),
            'image_type': image_type,
            'upload_time': datetime.utcnow(),
            'gender': sex,
            'age': age,
            'disease': disease
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
