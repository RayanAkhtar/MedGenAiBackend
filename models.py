from __init__ import db
from sqlalchemy.dialects.postgresql import ARRAY

class Competition(db.Model):
    __tablename__ = 'competitions'

    competition_id = db.Column(db.Integer, primary_key=True)
    competition_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)


class CompetitionUser(db.Model):
    __tablename__ = 'competition_users'

    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.competition_id'), nullable=False)
    user_id = db.Column(db.String(128), db.ForeignKey('users.user_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    competition = db.relationship('Competition', backref=db.backref('competition_users', lazy=True))
    user = db.relationship('Users', backref=db.backref('competition_users', lazy=True))


class Users(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.String(128), primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    level = db.Column(db.Integer, nullable=False, default=1)
    exp = db.Column(db.Integer, nullable=False, default=0)
    games_started = db.Column(db.Integer, nullable=False, default=0)
    games_won = db.Column(db.Integer, nullable=False, default=0)
    score = db.Column(db.Integer, nullable=False, default=0)


class Images(db.Model):
    __tablename__ = 'images'

    image_id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    image_type = db.Column(db.String(50), nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False)


class GameImages(db.Model):
    __tablename__ = 'game_images'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('images.image_id'), nullable=False)

    # Define relationships
    image = db.relationship('Images', 
                          backref=db.backref('game_images', lazy=True),
                          foreign_keys=[image_id])


class Game(db.Model):
    __tablename__ = 'games'

    game_id = db.Column(db.Integer, primary_key=True)
    game_mode = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    game_board = db.Column(db.String(50), nullable=False)
    game_status = db.Column(db.String(50), nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.String(128), db.ForeignKey('users.user_id'), nullable=False)

    # Define the relationship properly
    game_images = db.relationship('GameImages', 
                                backref=db.backref('game', lazy=True),
                                foreign_keys='GameImages.game_id')
    user_sessions = db.relationship('UserGameSession',
                                  backref=db.backref('game', lazy=True),
                                  foreign_keys='UserGameSession.game_id')
    creator = db.relationship('Users',
                            backref=db.backref('created_games', lazy=True),
                            foreign_keys=[created_by])


class UserGameSession(db.Model):
    """Tracks individual user sessions for each game"""
    __tablename__ = 'user_game_sessions'

    session_id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), nullable=False)
    user_id = db.Column(db.String(128), db.ForeignKey('users.user_id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    completion_time = db.Column(db.DateTime, nullable=True)
    session_status = db.Column(db.String(50), nullable=False)  # 'active', 'completed', 'abandoned'
    final_score = db.Column(db.Integer, nullable=True)
    correct_guesses = db.Column(db.Integer, nullable=True)
    total_guesses = db.Column(db.Integer, nullable=True)
    time_taken = db.Column(db.Integer, nullable=True)

    # Define relationships
    user = db.relationship('Users',
                         backref=db.backref('game_sessions', lazy=True),
                         foreign_keys=[user_id])


class UserGuess(db.Model):
    __tablename__ = 'user_guesses'

    guess_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('user_game_sessions.session_id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('images.image_id'), nullable=False)
    user_id = db.Column(db.String(128), db.ForeignKey('users.user_id'), nullable=False)
    user_guess_type = db.Column(db.String(50), nullable=False)
    date_of_guess = db.Column(db.DateTime, nullable=False)

    time_taken = db.Column(db.Float, nullable=True)

    # Relationships
    session = db.relationship('UserGameSession', backref=db.backref('guesses', lazy=True))
    image = db.relationship('Images', backref=db.backref('guesses', lazy=True))
    user = db.relationship('Users', backref=db.backref('guesses', lazy=True))


class FeedbackUser(db.Model):
    __tablename__ = 'feedback_users'

    feedback_id = db.Column(db.Integer, primary_key=True)
    guess_id = db.Column(db.Integer, db.ForeignKey('user_guesses.guess_id'), nullable=False)

    guess = db.relationship('UserGuess', backref=db.backref('feedback_users', lazy=True))


class Feedback(db.Model):
    __tablename__ = 'feedback'

    feedback_id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    msg = db.Column(db.String(255), nullable=False)
    resolved = db.Column(db.Boolean, default=False, nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)

    # 0 - Not confident at all     100 - Very Confident
    confidence = db.Column(db.Integer, nullable=False, default=50)

class Tag(db.Model):
    __tablename__ = 'tag'

    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable = False)

class UserTags(db.Model):
    __tablename__ = 'user_tags'

    user_id = db.Column(db.String(128), db.ForeignKey('users.user_id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.tag_id'), primary_key=True) 
