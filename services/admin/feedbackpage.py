from __init__ import db
from models import Images, Feedback, FeedbackUser, UserGuess
from sqlalchemy import func, case, desc, asc, text
from sqlalchemy.orm import aliased

def get_feedback_with_filters(image_type=None, resolved=None, sort_by=None, sort_order='asc', limit=20, offset=0):
    try:
        # Alias for Feedback table to avoid duplication due to joins
        feedback_alias = aliased(Feedback)

        # Base query
        query = (
            db.session.query(
                Images.image_id,
                Images.image_path,
                Images.image_type,
                # Use a subquery to count unresolved feedback
                func.count(case(
                    (func.coalesce(feedback_alias.resolved, False) == False, 1), 
                    else_=None
                )).label("unresolved_count"),
                func.max(feedback_alias.date_added).label("last_feedback_time"),
                Images.upload_time,
                Images.gender,
                Images.race,
                Images.age,
                Images.disease,
            )
            .outerjoin(UserGuess, UserGuess.image_id == Images.image_id)
            .outerjoin(FeedbackUser, FeedbackUser.guess_id == UserGuess.guess_id)
            .outerjoin(feedback_alias, feedback_alias.feedback_id == FeedbackUser.feedback_id)
            .group_by(
                Images.image_id, Images.image_path, Images.image_type, 
                Images.upload_time, Images.gender, Images.race, Images.age, Images.disease
            )
        )

        # Apply filters
        if image_type and image_type != "all":
            query = query.filter(Images.image_type == image_type)

        if resolved is not None:
            if resolved:
                query = query.having(func.count(case(
                    (func.coalesce(feedback_alias.resolved, False) == False, 1),
                    else_=None
                )) == 0)
            else:
                query = query.having(func.count(case(
                    (func.coalesce(feedback_alias.resolved, False) == False, 1),
                    else_=None
                )) > 0)

        # Sorting
        valid_sort_fields = {
            'last_feedback_time': func.max(feedback_alias.date_added),
            'unresolved_count': func.count(case(
                (func.coalesce(feedback_alias.resolved, False) == False, 1), 
                else_=None
            )),
            'upload_time': Images.upload_time,
            'image_id': Images.image_id,
        }

        if sort_by and sort_by in valid_sort_fields:
            order_func = asc if sort_order.lower() == 'asc' else desc
            query = query.order_by(order_func(valid_sort_fields[sort_by]))
        else:
            query = query.order_by(desc(func.max(feedback_alias.date_added)))

        # Apply limit and offset for pagination
        query = query.limit(limit).offset(offset)

        # Execute query
        results = query.all()

        # Format results
        feedback_data = [
            {
                'image_id': row.image_id,
                'image_path': row.image_path,
                'image_type': row.image_type,
                'unresolved_count': row.unresolved_count or 0,
                'last_feedback_time': row.last_feedback_time.strftime('%Y-%m-%d') if row.last_feedback_time else None,
                'upload_time': row.upload_time.strftime('%Y-%m-%d') if row.upload_time else None,
                'gender': row.gender,
                'race': row.race,
                'age': row.age,
                'disease': row.disease,
            }
            for row in results
        ]

        return feedback_data

    except Exception as e:
        print(f"Error fetching feedback: {e}")
        return []


def get_feedback_count(image_type=None, resolved=None):
    try:
        # Base query
        query = (
            db.session.query(func.count(func.distinct(Images.image_id)))
            .outerjoin(UserGuess, UserGuess.image_id == Images.image_id)
            .outerjoin(FeedbackUser, FeedbackUser.guess_id == UserGuess.guess_id)
            .outerjoin(Feedback, Feedback.feedback_id == FeedbackUser.feedback_id)
        )

        # Apply filters
        if image_type and image_type != "all":
            query = query.filter(Images.image_type == image_type)

        if resolved is not None:
            query = query.filter(Feedback.resolved == resolved)

        # Execute query
        total_count = query.scalar()

        return total_count or 0

    except Exception as e:
        print(f"Error fetching feedback count: {e}")
        return 0


def resolve_all_feedback_by_image(image_id: int):
    try:
        # Get all guesses associated with the image
        guess_ids = (
            db.session.query(UserGuess.guess_id)
            .filter(UserGuess.image_id == image_id)
            .all()
        )

        guess_ids = [g[0] for g in guess_ids]

        if not guess_ids:
            return {"error": "No guesses found for the given image_id"}

        # Update feedback as resolved
        db.session.query(Feedback).filter(
            Feedback.feedback_id.in_(
                db.session.query(FeedbackUser.feedback_id)
                .filter(FeedbackUser.guess_id.in_(guess_ids))
                .subquery()
            )
        ).update({Feedback.resolved: True}, synchronize_session=False)

        db.session.commit()
        return {"message": "All feedback for the image has been marked as resolved"}

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}
