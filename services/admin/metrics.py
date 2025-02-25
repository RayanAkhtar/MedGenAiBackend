from __init__ import db
from models import UserGuess, Images, Users
from sqlalchemy import func, case, text

def get_image_detection_accuracy():
    try:
        result = (
            db.session.query(
                func.to_char(UserGuess.date_of_guess, 'YYYY-MM').label('month'),
                (func.sum(
                    case(
                        (UserGuess.user_guess_type == Images.image_type, 1),
                        else_=0
                    )
                ) * 1.0) / func.count().label('accuracy')
            )
            .join(Images, UserGuess.image_id == Images.image_id)
            .filter(UserGuess.date_of_guess >= func.now() - text("INTERVAL '12 months'"))
            .group_by('month')
            .order_by('month')
            .all()
        )

        return [{'month': row[0], 'accuracy': row[1]} for row in result]
    
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}

def get_confusion_matrix():
    try:
        result = (
            db.session.query(
                func.sum(case(
                    (UserGuess.user_guess_type == 'real', UserGuess.user_guess_type == Images.image_type), 
                    else_=0)).label('truePositive'),
                func.sum(case(
                    (UserGuess.user_guess_type == 'ai', UserGuess.user_guess_type != Images.image_type), 
                    else_=0)).label('falsePositive'),
                func.sum(case(
                    (UserGuess.user_guess_type == 'real', UserGuess.user_guess_type != Images.image_type), 
                    else_=0)).label('falseNegative'),
                func.sum(case(
                    (UserGuess.user_guess_type == 'ai', UserGuess.user_guess_type == Images.image_type), 
                    else_=0)).label('trueNegative')
            )
            .join(Images, UserGuess.image_id == Images.image_id)
            .first()
        )

        return {
            "truePositive": result.truePositive,
            "falsePositive": result.falsePositive,
            "falseNegative": result.falseNegative,
            "trueNegative": result.trueNegative
        }

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}

def get_ml_metrics():
    try:
        result = (
            db.session.query(
                func.sum(case(
                    (UserGuess.user_guess_type == Images.image_type, UserGuess.user_guess_type == 'real'), 
                    else_=0)).label('true_positive'),
                func.sum(case(
                    (UserGuess.user_guess_type != Images.image_type, UserGuess.user_guess_type == 'real'), 
                    else_=0)).label('false_positive'),
                func.sum(case(
                    (UserGuess.user_guess_type == Images.image_type, UserGuess.user_guess_type == 'ai'), 
                    else_=0)).label('true_negative'),
                func.sum(case(
                    (UserGuess.user_guess_type != Images.image_type, UserGuess.user_guess_type == 'ai'), 
                    else_=0)).label('false_negative')
            )
            .join(Images, UserGuess.image_id == Images.image_id)
            .first()
        )

        if not result:
            return {"error": "No data found"}

        true_positive = result.true_positive or 0
        false_positive = result.false_positive or 0
        true_negative = result.true_negative or 0
        false_negative = result.false_negative or 0

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
        result = (
            db.session.query(
                UserGuess.user_id,
                Users.username,
                func.avg(case(
                    (UserGuess.user_guess_type == Images.image_type, 1), 
                    else_=0)).label('accuracy')
            )
            .join(Images, UserGuess.image_id == Images.image_id)
            .join(Users, Users.user_id == UserGuess.user_id)
            .group_by(UserGuess.user_id, Users.username)
            .order_by(func.avg(case(
                    (UserGuess.user_guess_type == Images.image_type, 1), 
                    else_=0)).desc())
            .limit(10)
            .all()
        )

        return [{'user_id': row[0], 'username': row[1], 'accuracy': row[2]} for row in result]

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}

def get_image_difficulty():
    try:
        result = (
            db.session.query(
                Images.image_id,
                Images.image_path,
                func.count().label('total_guesses'),
                func.sum(case(
                    (UserGuess.user_guess_type != Images.image_type, 1), 
                    else_=0)).label('incorrect_guesses'),
                (func.sum(case(
                    (UserGuess.user_guess_type != Images.image_type, 1), 
                    else_=0)) * 1.0 / func.count()).label('difficulty_score')
            )
            .join(UserGuess, UserGuess.image_id == Images.image_id)
            .group_by(Images.image_id)
            .order_by((func.sum(case(
                    (UserGuess.user_guess_type != Images.image_type, 1), 
                    else_=0)) * 1.0 / func.count()).desc())
            .all()
        )

        return [{'image_id': row[0], 'image_path': row[1], 'total_guesses': row[2], 'incorrect_guesses': row[3], 'difficulty_score': row[4]} for row in result]

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}
