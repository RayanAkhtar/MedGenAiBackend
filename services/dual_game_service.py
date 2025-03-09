from __init__ import db
from models import *
from sqlalchemy import text, bindparam, func
from datetime import datetime 
from flask import jsonify
import logging

def create_game(game_mode, game_status, username, game_board):
    try:
        created_by = Users.query.filter_by(username=username).first()
        if not created_by:
            return None, {"error": "User not found"}, 404

        game = Game(
            game_board=game_board,
            game_mode=game_mode,
            date_created=datetime.utcnow(),
            created_by=created_by.user_id,
            game_status=game_status
        )
        db.session.add(game)
        db.session.commit()

        game_id = game.game_id
        game_code = GameCode(
            game_id=game_id
        )
        return game_id, game_code
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        logging.error(f"Error creating game: {e}")
        return None, {"error": f"Error creating game"}, 500

def create_dual_game(game_mode, game_status, username, image_urls):
    try:
        images_paths = [image_url.split('admin/')[-1] for image_url in image_urls]
        print(images_paths)
        image_ids = Images.query.filter(Images.image_path.in_(images_paths)).all()

        if not image_ids:
            return {"error": "No images found for the provided URLs"}, 400

        game_id, game_code, code = create_game(game_mode, game_status, username, game_board='dual')
        if not game_id:
            return game_code, code  # Return the error from create_game

        for image_id in image_ids:
            game_image = GameImages(
                game_id=game_id,
                image_id=image_id.image_id
            )
            db.session.add(game_image)
        db.session.commit()
        return {'game_code': game_code}, 201
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        logging.error(f"Error creating dual game: {e}")
        return {"error": f"Error creating dual game"}, 500
