from models import Users, Images, UserGuess
from __init__ import db
from typing import Tuple, List
import uuid
import datetime

class GameService:
    def __init__(self):
        self.active_games = {}

    def initialize_game(self, game_type: str, image_count: int, user_id: int) -> Tuple[str, List[dict]]:
        """
        Initialize a new game session for a user
        
        Args:
            game_type (str): Type of game (e.g., 'classic')
            image_count (int): Number of images for the game
            user_id (int): Database user ID
            
        Returns:
            Tuple[str, List[dict]]: Game ID and list of selected images
        """
        # Generate unique game ID
        game_id = str(uuid.uuid4())
        print (f"Game ID: {game_id}")
        # Get random images from database
        # images = Images.query.filter_by(
        #     image_type=game_type
        # ).order_by(db.func.random()).limit(image_count).all()
        # print (f"Images: {images}")
        # if not images:
        #     raise ValueError(f"No images found for game type: {game_type}")
        
        # Format images for response
        # image_data = [{
        #     'id': img.image_id,
        #     'path': img.image_path,
        #     'type': img.image_type
        # } for img in images]

        # Generate dummy image data instead
        image_data = []
        for i in range(image_count):
            image_data.append({
                'id': i+1,
                'path': f'/images/{game_type}/dummy_image_{i+1}.jpg',
                'type': game_type
            })
        
        # Store game session
        self.active_games[game_id] = {
            'game_id': game_id,
            'user_id': user_id,
            'type': game_type,
            'image_count': image_count,
            'selected_images': image_data,
            'status': 'active',
            'created_at': datetime.datetime.now(),
            'last_accessed': datetime.datetime.now()
        }
        
        return game_id, image_data