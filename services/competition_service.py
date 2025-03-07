from datetime import datetime
import random
import string
from typing import Dict, Any

from __init__ import db
from models import Game, Images, GameImages, Competition, CompetitionGame
from services.game_service import GameService

class CompetitionService:
    def __init__(self):
        self.game_service = GameService()
    
    def create_competition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new competition with associated game
        
        Args:
            data (Dict): Competition data including:
                - competition_name: Competition name
                - end_date: Date when competition expires
                - game_id: Game code (optional)
                - game_board: Type of game
            
        Returns:
            Dict: Created competition data
        """
        try:
            # Extract competition data
            competition_name = data.get('competition_name')
            end_date_str = data.get('end_date')
            game_code = data.get('game_id')
            game_type = data.get('game_board')
            
            # Validate required fields
            if not competition_name:
                raise ValueError("Competition name is required")
                
            # Parse end date
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Invalid end date format. Use YYYY-MM-DD")
            else:
                # Default end date (30 days from now)
                end_date = datetime.now().replace(hour=23, minute=59, second=59)
                end_date = end_date.replace(day=end_date.day + 30)
            
            # Set start date to now
            start_date = datetime.now()
            
            # Create a new game for this competition
            # Get random images (10 real, 10 AI)
            real_images = Images.query.filter_by(image_type='real').order_by(db.func.random()).limit(10).all()
            ai_images = Images.query.filter_by(image_type='ai').order_by(db.func.random()).limit(10).all()
            
            # Create game
            game = Game(
                game_mode=game_type,
                date_created=datetime.now(),
                game_status='active',
                created_by="admin",
                expiry_date=end_date
            )
            db.session.add(game)
            db.session.flush()  # Get the game ID
            
            # Add images to game
            for image in real_images + ai_images:
                game_image = GameImages(
                    game_id=game.game_id,
                    image_id=image.image_id
                )
                db.session.add(game_image)
            
            # Create competition - using only fields that exist in your model
            competition = Competition(
                competition_name=competition_name,
                start_date=start_date,
                end_date=end_date
            )
            db.session.add(competition)
            db.session.flush()  # Get the competition ID
            
            # Create a CompetitionGame relationship
            competition_game = CompetitionGame(
                competition_id=competition.competition_id,
                game_id=game.game_id
            )
            db.session.add(competition_game)
            
            # Commit changes
            db.session.commit()
            
            # Use provided game code or generate one based on competition ID
            if not game_code:
                game_code = f"{competition.competition_id:07d}"
            
            # Return competition data
            return {
                'competition_id': competition.competition_id,
                'competition_name': competition.competition_name,
                'start_date': competition.start_date.isoformat(),
                'end_date': competition.end_date.isoformat(),
                'game_id': game.game_id,
                'game_code': game_code,
                'game_mode': game.game_mode
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating competition: {str(e)}")
            raise
