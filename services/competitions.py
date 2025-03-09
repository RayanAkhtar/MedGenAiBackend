from __init__ import db
from models import *
from sqlalchemy import text, bindparam, func
from datetime import datetime 
from flask import jsonify
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
# Admin only
def create_competition(name, expiry ,game_code):
    """
    Create a new game first then gets the game id from it.
    Creates a new competition using that same id.
    """
    logger.info(f"Creating competition : {name}")

    game = Game.query.filter_by(game_id=game_code).first()
    if not game:
        return jsonify({'message': 'Game not found'}), 404
    comp = Competition.query.filter_by(competition_id=game_code).first()

    if comp:
        return jsonify({'message': 'Competition already exists'}), 400
    try:
        
        real_expiry = expiry if not game.expiry_date else game.expiry_date
        
        new_competition = Competition(
            competition_id=game_code,
            competition_name=name,
            start_date=datetime.now(),
            end_date=real_expiry,
        )

        db.session.add(new_competition)
        db.session.commit()
        return jsonify({'message': 'Competition created successfully', 'competition_id': new_competition.competition_id}), 200
    except Exception as e:
        logger.error(f"Error creating competition: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_all_competitions():
    """
    Retrieves all competitions with their associated game boards.
    """
    try:
        competitions = db.session.query(Competition, Game.game_board).join(Game, Competition.competition_id == Game.game_id).all()
        
        result = [
            {
                'id': comp.competition_id,
                'name': comp.competition_name,
                'start_date': comp.start_date,
                'end_date': comp.end_date,
                'game_board': game_board 
            } for comp, game_board in competitions
        ]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_competition(game_id):
    """
    Retrieves competition details by ID, including the top player based on the highest score.
    """
    try:
        competition = Competition.query.filter_by(competition_id=game_id).first()
        if not competition:
            return jsonify({'message': 'Competition not found'}), 404

        # Get top player by score from CompetitionUser
        top_player_data = (
            db.session.query(Users.username, CompetitionUser.score)
            .join(CompetitionUser, Users.user_id == CompetitionUser.user_id)
            .filter(CompetitionUser.competition_id == game_id)
            .order_by(CompetitionUser.score.desc())
            .first()
        )

        top_player = {
            'username': top_player_data.username,
            'score': top_player_data.score
        } if top_player_data else None

        result = {
            'id': competition.competition_id,
            'name': competition.competition_name,
            'start_date': competition.start_date,
            'expiry': competition.end_date,
        }
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def submit_competition_score(competition_id, user_id, score):
    """
    Creates a new competition and returns the competition ID.
    """
    try:
        new_competition_user = CompetitionUser(
            competition_id=competition_id,
            user_id=user_id,
            score=score
        )
        db.session.add(new_competition_user)
        db.session.commit()
        return jsonify({'message': 'CompetitionUser enterred successfully', 'competition_user_id': new_competition_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_game_by_game_id(game_id):
    try:
        # Fetch the game from the database
        game = db.session.query(Game).filter_by(game_id=game_id).first()
        
        # If game not found, return an error message
        if not game:
            return {"error": "Game not found"}, 404
        
        created_by = db.session.query(Users).filter_by(user_id=game.created_by).first()
        game_code = db.session.query(GameCode).filter_by(game_id=game_id).first()
        
        # Construct the response
        game_data = {
            "game_id": game.game_id,
            "game_mode": game.game_mode,
            "date_created": game.date_created,
            "game_board": game.game_board,
            "game_status": game.game_status,
            "expiry_date": game.expiry_date,
            "created_by": created_by.username if created_by else None,
            "game_code": game_code.game_code if game_code else None
        }
        
        return game_data, 200
    except Exception as e:
        return {"error": str(e)}, 500
