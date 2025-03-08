from __init__ import db
from models import *
from sqlalchemy import text, bindparam, func, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime 
import os
from flask import jsonify, flash
from werkzeug.utils import secure_filename
from decimal import Decimal


def get_users_with_filters(sort_by=None, sort_order='asc', limit=20, offset=0, level=None, min_games_won=None, max_games_won=None, min_score=None, max_score=None):
    try:
        # Start the query string
        query_str = """
            SELECT 
                users.user_id,
                users.username,
                users.level,
                users.games_started,
                users.games_won,
                users.score,
                ROUND(COALESCE(
                    (COUNT(CASE WHEN user_guesses.user_guess_type = images.image_type THEN 1 END) * 100.0) / NULLIF(COUNT(user_guesses.guess_id), 0),
                    0
                ), 2) AS accuracy,
                COALESCE(COUNT(user_guesses.guess_id), 0) as engagement
            FROM users
            LEFT JOIN user_guesses ON users.user_id = user_guesses.user_id
            LEFT JOIN images ON user_guesses.image_id = images.image_id
            WHERE 1=1
        """
        # Dictionary to store query parameters
        params = {'limit': limit, 'offset': offset}

        # Apply filters conditionally
        if level is not None:
            query_str += " AND users.level = :level"
            params['level'] = level

        if min_games_won is not None:
            query_str += " AND users.games_won >= :min_games_won"
            params['min_games_won'] = min_games_won

        if max_games_won is not None:
            query_str += " AND users.games_won <= :max_games_won"
            params['max_games_won'] = max_games_won

        if min_score is not None:
            query_str += " AND users.score >= :min_score"
            params['min_score'] = min_score

        if max_score is not None:
            query_str += " AND users.score <= :max_score"
            params['max_score'] = max_score

        # Define valid sorting fields
        valid_sort_fields = ['user_id', 'username', 'level', 'games_won', 'score', 'accuracy', 'engagement']
        
        # Apply sorting if a valid sort_by field is provided
        if sort_by in valid_sort_fields:
            query_str += f" GROUP BY users.user_id, users.username, users.level, users.games_started, users.games_won, users.score"
            query_str += f" ORDER BY {sort_by} {sort_order.upper()}"
        else:
            query_str += " GROUP BY users.user_id, users.username, users.level, users.games_started, users.games_won, users.score"
            query_str += " ORDER BY users.user_id ASC"  # Default sorting by user_id

        # Add LIMIT and OFFSET for pagination
        query_str += " LIMIT :limit OFFSET :offset"

        # Execute the query
        query = text(query_str)
        result = db.session.execute(query, params)

        # Process and format the results
        users_data = []
        for row in result.mappings():
            users_data.append({
                'user_id': row['user_id'],
                'username': row['username'],
                'level': row['level'],
                'games_started': row['games_started'],
                'games_won': row['games_won'],
                'score': row['score'],
                'accuracy': row['accuracy'],
                'engagement': row['engagement']
            })

        return users_data
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []


def get_users_ordered():
    try:
        query = text("""
            SELECT 
                user_id, username, level, exp, games_started, games_won, score
            FROM users
            ORDER BY user_id;
        """)
        result = db.session.execute(query)
        db.session.commit()

        users = []
        for row in result:
            users.append({column: value for column, value in zip(result.keys(), row)})

        return users

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}
    
def get_user_data_by_username(username):
    try:
        query = text("""
            SELECT
                u.user_id,u.username,u.level,u.exp,u.games_started,u.games_won,u.score,

                COALESCE(g.total_images_guessed, 0) AS total_images_guessed,
                COALESCE(g.correct_guesses, 0) AS correct_guesses,
                COALESCE(g.accuracy_percentage, 0) AS accuracy_percentage

            FROM users u
            LEFT JOIN (
                SELECT
                    ug.user_id,
                    COUNT(*) AS total_images_guessed,
                    SUM(
                        CASE WHEN ug.user_guess_type = i.image_type
                             THEN 1 ELSE 0 END
                    ) AS correct_guesses,

                    -- Calculate accuracy percentage
                    CASE
                        WHEN COUNT(*) = 0 THEN 0
                        ELSE (
                            SUM(
                                CASE WHEN ug.user_guess_type = i.image_type
                                     THEN 1 ELSE 0 END
                            ) * 100.0
                            / COUNT(*)
                        )
                    END AS accuracy_percentage

                FROM user_guesses ug
                JOIN images i ON ug.image_id = i.image_id
                GROUP BY ug.user_id
            ) AS g ON g.user_id = u.user_id

            WHERE u.username = CAST(:username AS VARCHAR)
        """)

        result = db.session.execute(query, {'username': str(username)})
        row = result.fetchone()

        if not row:
            return {"error": "User not found"}, 404

        # Convert the row to a dictionary
        user_data = dict(zip(result.keys(), row))

        return user_data, 200

    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500

def get_game_by_game_code(game_code):
    try:
        game_code_entry = db.session.query(GameCode).filter_by(game_code=game_code).first()
        if not game_code_entry:
            return {"error": "Invalid game code"}, 404
        game_id = game_code_entry.game_id        # Fetch the game from the database
        game = db.session.query(Game).filter_by(game_id=game_id).first()
        created_by = db.session.query(Users).filter_by(user_id=game.created_by).first()

        if not game:
            return {"error": "Game not found"}

        game_data = {
            "game_code": game_code,
            "game_mode": game.game_mode,
            "date_created": game.date_created,
            "game_board": game.game_board,
            "game_status": game.game_status,
            "expiry_date": game.expiry_date,
            "created_by": created_by.username,
        }

        return game_data, 200
    except Exception as e:
        return {"error": str(e)}, 404
    

def create_user_game_session(game_code, user_name):
    """Creates a new UserGameSession and commits it to the database."""
    return create_multiple_game_sessions(game_code, [user_name])
    
def create_multiple_game_sessions(game_code, usernames):
    """Creates multiple UserGameSession objects for a given game_id and list of user_ids."""
    from sqlalchemy.exc import SQLAlchemyError
    try:
        new_sessions = []
        game_code_entry = db.session.query(GameCode).filter_by(game_code=game_code).first()
        if not game_code_entry:
            return {"error": "Invalid game code"}, 404
        game_id = game_code_entry.game_id
        
        users = db.session.query(Users).filter(Users.username.in_(usernames)).all()
        if not users or len(users) != len(usernames):
            return {"error": "One or more usernames are invalid"}, 404

        user_ids = {user.user_id for user in users}
        existing_sessions = db.session.query(UserGameSession.user_id).filter(
            and_(
                UserGameSession.game_id == game_id,
                UserGameSession.user_id.in_(user_ids)
            )
        ).all()
        assigned_user_ids = {session.user_id for session in existing_sessions}
        new_user_ids = user_ids - assigned_user_ids

        for user_id in new_user_ids:
            new_session = UserGameSession(
                game_id=game_id,
                user_id=user_id,
                start_time=datetime.now(),
                session_status="active"  # Default status
            )
            new_sessions.append(new_session)

        if new_sessions:
             # Add all sessions to the session and commit
            db.session.add_all(new_sessions)
            db.session.commit()
        return new_sessions, 200  # Return the created sessions

    except IntegrityError:
        db.session.rollback()
        return {'error': 'Database integrity error'}, 409
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error creating user game sessions: {e}")
        return {'error': str(e)}, 404  # Return None if an error occurs

def get_assigned_games_by_username(username):
    try:
        # Perform a single query to fetch game data for a user based on username
        games = db.session.query(Game).join(UserGameSession, Game.game_id == UserGameSession.game_id) \
            .join(Users, Users.user_id == UserGameSession.user_id) \
            .filter(Users.username == username).all()

        # Prepare the game data
        game_data = [{
            'game_id': game.game_id,
            'game_mode': game.game_mode,
            'game_board': game.game_board,
            'game_status': game.game_status,
            'expiry_date': game.expiry_date,
            'active': games.session_status == 'active'
        } for game in games]

        return game_data

    except SQLAlchemyError as e:
        return {'error': "Error accessing database"}, 404
