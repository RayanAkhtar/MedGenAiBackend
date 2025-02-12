from __init__ import db


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
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
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


class UserGuess(db.Model):
    __tablename__ = 'user_guesses'

    guess_id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.image_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user_guess_type = db.Column(db.String(50), nullable=False)
    date_of_guess = db.Column(db.DateTime, nullable=False)

    image = db.relationship('Images', backref=db.backref('user_guesses', lazy=True))
    user = db.relationship('Users', backref=db.backref('user_guesses', lazy=True))


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
