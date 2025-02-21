from models import Users, Images, UserGuess
from __init__ import db
from typing import Tuple, List, Dict
import uuid
import datetime
import random
from services.images import get_images_rand

class GameService:
    def __init__(self):
        self.active_games = {}

    def initialize_classic_game(self, image_count: int, user_id: str) -> Tuple[str, List[Dict]]:
        """
        Initialize a classic game with mixed real and AI images
        
        Args:
            image_count (int): Total number of images for the game
            user_id (str): User's ID
            
        Returns:
            Tuple[str, List[dict]]: Game ID and list of image URLs
        """
        try:
            game_id = str(uuid.uuid4())
            print(f"Initializing classic game {game_id} for user {user_id}")
            print(f"Requested image count: {image_count}")

            # Get equal number of real and AI images
            half_count = max(image_count // 2, 1)
            print(f"Fetching {half_count} real images and {half_count} AI images")
            
            real_images = get_images_rand(half_count, 'real')
            print(f"Got {len(real_images)} real images")
            
            ai_images = get_images_rand(half_count, 'ai')
            print(f"Got {len(ai_images)} AI images")

            # Format images with their types
            image_data = (
                [{'url': url, 'type': 'real'} for url in real_images] +
                [{'url': url, 'type': 'ai'} for url in ai_images]
            )
            
            print(f"Total images after combining: {len(image_data)}")
            random.shuffle(image_data)

            # Store game session
            self.active_games[game_id] = {
                'game_id': game_id,
                'user_id': user_id,
                'type': 'classic',
                'image_count': len(image_data),
                'selected_images': image_data,
                'status': 'active',
                'created_at': datetime.datetime.now(),
                'last_accessed': datetime.datetime.now()
            }

            print(f"Classic game initialized with {len(image_data)} images")
            return game_id, image_data

        except Exception as e:
            print(f"Error initializing classic game: {str(e)}")
            raise

    def get_game(self, game_id: str) -> Dict:
        """
        Get game session data
        
        Args:
            game_id (str): The game's unique identifier
            
        Returns:
            Dict: Game session data
        """
        game = self.active_games.get(game_id)
        if not game:
            raise ValueError(f"Game not found: {game_id}")
        
        game['last_accessed'] = datetime.datetime.now()
        return game

    def update_game_status(self, game_id: str, status: str) -> None:
        """
        Update game status
        
        Args:
            game_id (str): The game's unique identifier
            status (str): New status for the game
        """
        game = self.get_game(game_id)
        game['status'] = status
        game['last_accessed'] = datetime.datetime.now()