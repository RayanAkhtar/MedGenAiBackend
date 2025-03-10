import uuid
from __init__ import db
from models import *
from services.images import get_images_rand
from sqlalchemy import text, bindparam, func
from datetime import datetime 
from flask import jsonify, request
import logging

def create_game(game_mode, game_status, username, game_board):
    try:
        created_by = Users.query.filter_by(username=username).first()
        if not created_by:
            return None, {"error": "User not found"}, 404

        # Create and add the game
        game = Game(
            game_board=game_board,
            game_mode=game_mode,
            date_created=datetime.utcnow(),
            created_by=created_by.user_id,
            game_status=game_status
        )
        db.session.add(game)
        db.session.flush()

        # Create game_code based on the new game_id
        game_code = GameCode(
            game_id=game.game_id
        )
        db.session.add(game_code) 
        db.session.commit() 

        return game.game_id, game_code.game_code, 201
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
            db.session.flush()  

        db.session.commit()  # Commit all changes together

        return {'game_code': game_code}, 201
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        logging.error(f"Error creating dual game: {e}")
        return {"error": f"Error creating dual game"}, 500


def initialize_dual_game_backend(num_rounds, user_id):
    """
    Backend logic to initialize a dual game with specified number of rounds and user ID.
    
    Args:
        num_rounds (int): Number of rounds in the game
        user_id (str): User's ID who is creating the game
        
    Returns:
        dict: Game data including game code, mode, rounds, and settings
    """
    try:
        real_count = num_rounds
        ai_count = num_rounds
        
        print(f"Fetching {real_count} real images and {ai_count} AI images")
        
        real_images = get_images_rand(real_count, 'real')
        print(f"Got {len(real_images)} real images")
        
        ai_images = get_images_rand(ai_count, 'ai')
        print(f"Got {len(ai_images)} AI images")
        
        # Create new game in database
        new_game = Game(
            game_mode='dual',
            date_created=datetime.utcnow(),
            game_board='dual',
            game_status='active',
            expiry_date=datetime.utcnow() + datetime.timedelta(days=1),  # Game expires in 24 hours
            created_by=user_id,
        )
        db.session.add(new_game)
        db.session.flush()  # This will show errors before commit
        print(f"Game created successfully with ID: {new_game.game_id}")
        
        # Generate a unique game code
        game_code = str(uuid.uuid4())[:8].upper()
        # Create GameCode entry
        game_code_entry = GameCode(
            game_id=new_game.game_id,
            game_code=game_code
        )
        db.session.add(game_code_entry)
        
        # Format images with their types and create GameImages entries
        rounds = []
        for i in range(num_rounds):
            round_images = [
                {
                    'id': str(uuid.uuid4()),
                    'url': real_images[i],
                    'isCorrect': True
                },
                {
                    'id': str(uuid.uuid4()),
                    'url': ai_images[i],
                    'isCorrect': False
                }
            ]
            rounds.append({
                'roundId': str(uuid.uuid4()),
                'images': round_images
            })
            
            # Add images to GameImages table
            for img in round_images:
                image_path = img['url'].split('/api/images/view/')[-1]
                image = Images.query.filter_by(image_path=image_path).first()
                if image:
                    game_image = GameImages(
                        game_id=new_game.game_id,
                        image_id=image.image_id
                    )
                    db.session.add(game_image)
        
        db.session.commit()
        
        game_data = {
            'gameCode': game_code,
            'gameMode': 'dual',
            'rounds': rounds,
            'settings': {
                'timerPerRound': 60,
                'maxRounds': num_rounds
            }
        }
        
        return game_data, 201
    
    except Exception as e:
        print(f"Error initializing dual game: {str(e)}")
        db.session.rollback()
        return {"error": f"Error initializing dual game"}, 500

def get_dual_game_backend(game_code):
    """
    Backend logic to fetch dual game data using the game code.
    
    Args:
        game_code (str): Code of the game to fetch
        
    Returns:
        dict: Game data including game code, mode, rounds, and settings
    """
    try:
        game_code_entry = GameCode.query.filter_by(game_code=game_code).first()
        if not game_code_entry:
            return {"error": "Game not found"}, 404
        
        game = Game.query.filter_by(game_id=game_code_entry.game_id).first()
        if not game:
            return {"error": "Game not found"}, 404
        
        rounds = []
        for game_image in game.game_images:
            image = game_image.image
            round_id = str(uuid.uuid4())
            rounds.append({
                'roundId': round_id,
                'images': [
                    {
                        'id': str(uuid.uuid4()),
                        'url': f"/api/images/view/{image.image_path}",
                        'isCorrect': image.image_type == 'real'
                    },
                    {
                        'id': str(uuid.uuid4()),
                        'url': f"/api/images/view/{image.image_path}",
                        'isCorrect': image.image_type == 'ai'
                    }
                ]
            })
        
        game_data = {
            'gameCode': game_code,
            'gameMode': game.game_mode,
            'rounds': rounds,
            'settings': {
                'timerPerRound': 60,
                'maxRounds': len(rounds)
            }
        }
        
        return game_data, 200
    
    except Exception as e:
        print(f"Error fetching dual game: {str(e)}")
        return {"error": f"Error fetching dual game"}, 500
