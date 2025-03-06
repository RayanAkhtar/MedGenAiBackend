from models import db, Users, UserGameSession, UserGuess, Images

def get_accuracy_for_user(username: str) -> float:
    user = Users.query.filter_by(username=username).first()
    if not user:
        raise ValueError(f"User {username} not found")

    total_guesses = db.session.query(UserGuess).join(UserGameSession).filter(UserGameSession.user_id == user.user_id).count()

    correct_guesses = db.session.query(UserGuess).join(UserGameSession).join(Images).filter(
        UserGameSession.user_id == user.user_id,
        UserGuess.user_guess_type == Images.image_type
    ).count()

    if total_guesses == 0:
        return 0.0

    accuracy = (correct_guesses / total_guesses) * 100
    return accuracy



def get_total_images_attempted_for_user(username: str) -> int:
    user = Users.query.filter_by(username=username).first()
    if not user:
        raise ValueError(f"User {username} not found")

    total_images_attempted = db.session.query(UserGuess).join(UserGameSession).filter(UserGameSession.user_id == user.user_id).count()
    
    return total_images_attempted
