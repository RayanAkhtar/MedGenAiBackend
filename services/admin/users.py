from sqlalchemy import func
from models import db, Users, UserGameSession, UserGuess, Images, UserTags, Tag

def get_accuracy_for_user(username: str, tag_names=None) -> float:
    user = Users.query.filter_by(username=username).first()
    if not user:
        raise ValueError(f"User {username} not found")

    query = db.session.query(
        func.count(func.distinct(UserGuess.guess_id)).label("total_guesses"),
        func.count(func.distinct(UserGuess.guess_id)).filter(UserGuess.user_guess_type == Images.image_type).label("correct_guesses")
    ).join(UserGameSession).join(Images).filter(UserGameSession.user_id == user.user_id)

    if tag_names:
        tag_names = [t.lower() for t in tag_names]
        query = query.join(UserTags).join(Tag).filter(func.lower(Tag.name).in_(tag_names))

    result = query.one_or_none()

    if result:
        total_guesses = result.total_guesses
        correct_guesses = result.correct_guesses
    else:
        total_guesses = 0
        correct_guesses = 0

    if total_guesses == 0:
        return 0.0

    accuracy = (correct_guesses / total_guesses) * 100
    return round(accuracy, 2)


def get_total_images_attempted_for_user(username: str, tag_names=None) -> int:
    user = Users.query.filter_by(username=username).first()
    if not user:
        raise ValueError(f"User {username} not found")

    query = db.session.query(func.count(func.distinct(UserGuess.guess_id)).label("total_images_attempted")
    ).join(UserGameSession).filter(UserGameSession.user_id == user.user_id)

    if tag_names:
        tag_names = [t.lower() for t in tag_names]
        query = query.join(UserTags).join(Tag).filter(func.lower(Tag.name).in_(tag_names))

    result = query.one_or_none()

    if result:
        total_images_attempted = result.total_images_attempted
    else:
        total_images_attempted = 0

    return total_images_attempted
