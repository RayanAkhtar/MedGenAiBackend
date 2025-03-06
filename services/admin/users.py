from sqlalchemy import func
from models import db, Users, UserGameSession, UserGuess, Images, UserTags, Tag

def get_accuracy_for_user(username: str) -> float:
    user = Users.query.filter_by(username=username).first()
    if not user:
        raise ValueError(f"User {username} not found")

    total_guesses = db.session.query(func.count(func.distinct(UserGuess.guess_id))).join(UserGameSession).filter(
        UserGameSession.user_id == user.user_id
    ).scalar()

    correct_guesses = db.session.query(func.count(func.distinct(UserGuess.guess_id))).join(UserGameSession).join(Images).filter(
        UserGameSession.user_id == user.user_id,
        UserGuess.user_guess_type == Images.image_type
    ).scalar()

    if total_guesses == 0:
        return 0.0

    accuracy = (correct_guesses / total_guesses) * 100
    return round(accuracy, 2)


def get_total_images_attempted_for_user(username: str) -> int:
    user = Users.query.filter_by(username=username).first()
    if not user:
        raise ValueError(f"User {username} not found")

    total_images_attempted = db.session.query(func.count(func.distinct(UserGuess.guess_id))).join(UserGameSession).filter(
        UserGameSession.user_id == user.user_id
    ).scalar()
    
    return total_images_attempted
