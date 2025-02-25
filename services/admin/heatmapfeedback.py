from __init__ import db
from models import Images, Feedback, FeedbackUser, UserGuess
from sqlalchemy import func, case, text

def get_image_by_id(image_id):
    try:
        image = (
            db.session.query(Images.image_id, Images.image_path, Images.image_type, Images.upload_time)
            .filter(Images.image_id == image_id)
            .first()
        )

        return {"image_id": image.image_id, "image_path": image.image_path, "image_type": image.image_type, "upload_time": image.upload_time} if image else None

    except Exception as e:
        db.session.rollback()
        print(f"Error fetching image by id: {e}")
        return None


def get_matching_feedback_for_image(image_id):
    try:
        result = (
            db.session.query(
                Feedback.feedback_id, Feedback.msg, Feedback.x, Feedback.y
            )
            .join(FeedbackUser, FeedbackUser.feedback_id == Feedback.feedback_id)
            .join(UserGuess, FeedbackUser.guess_id == UserGuess.guess_id)
            .join(Images, UserGuess.image_id == Images.image_id)
            .filter(UserGuess.image_id == image_id, UserGuess.user_guess_type == Images.image_type)
            .all()
        )

        return [{"feedback_id": row.feedback_id, "msg": row.msg, "x": row.x, "y": row.y} for row in result]

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}


def get_image_confusion_matrix(image_id):
    try:
        result = (
            db.session.query(
                func.sum(case(
                    [(UserGuess.user_guess_type == 'real', Images.image_type == 'real')], 
                    else_=0)).label('truePositive'),
                func.sum(case(
                    [(UserGuess.user_guess_type == 'ai', Images.image_type == 'real')], 
                    else_=0)).label('falsePositive'),
                func.sum(case(
                    [(UserGuess.user_guess_type == 'real', Images.image_type == 'ai')], 
                    else_=0)).label('falseNegative'),
                func.sum(case(
                    [(UserGuess.user_guess_type == 'ai', Images.image_type == 'ai')], 
                    else_=0)).label('trueNegative')
            )
            .join(Images, UserGuess.image_id == Images.image_id)
            .filter(Images.image_id == image_id)
            .first()
        )

        return {
            "truePositive": result.truePositive or 0,
            "falsePositive": result.falsePositive or 0,
            "falseNegative": result.falseNegative or 0,
            "trueNegative": result.trueNegative or 0
        } if result else {"error": "No data found"}

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}
