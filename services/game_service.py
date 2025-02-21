from models import Users, Images, UserGuess, Game, GameImages, UserGameSession
from __init__ import db
from typing import Tuple, List, Dict
import uuid
import datetime
import random
from services.images import get_images_rand

class GameService:
    def __init__(self):
        self.active_sessions = {}

    def initialize_classic_game(self, image_count: int, user_id: str) -> Tuple[str, List[Dict]]:
        """
        Initialize a classic game with mixed real and AI images
        
        Args:
            image_count (int): Total number of images for the game
            user_id (str): User's ID who is creating the game
            
        Returns:
            Tuple[str, List[dict]]: Game ID and list of image URLs
        """
        try:
            print(f"Initializing classic game for user {user_id}")
            print(f"Requested image count: {image_count}")

            # Get equal number of real and AI images
            half_count = max(image_count // 2, 1)
            print(f"Fetching {half_count} real images and {half_count} AI images")
            
            real_images = get_images_rand(half_count, 'real')
            print(f"Got {len(real_images)} real images")
            
            ai_images = get_images_rand(half_count, 'ai')
            print(f"Got {len(ai_images)} AI images")

            # Create new game in database
            new_game = Game(
                game_mode='classic',
                date_created=datetime.datetime.now(),
                game_board='classic',
                game_status='active',
                expiry_date=datetime.datetime.now() + datetime.timedelta(days=1),  # Game expires in 24 hours
                created_by=user_id
            )
            db.session.add(new_game)
            db.session.flush()  # Get the game_id

            # Format images with their types and create GameImages entries
            image_data = []
            for url in real_images + ai_images:
                # Get image_id from URL
                image_path = url.split('/api/images/view/')[-1]
                image = Images.query.filter_by(image_path=image_path).first()
                
                if image:
                    # Create GameImages entry
                    game_image = GameImages(
                        game_id=new_game.game_id,
                        image_id=image.image_id
                    )
                    db.session.add(game_image)
                    
                    # Add to image_data for response
                    image_data.append({
                        'url': url,
                        'type': image.image_type
                    })

            # Create initial game session for creator
            user_session = UserGameSession(
                game_id=new_game.game_id,
                user_id=user_id,
                start_time=datetime.datetime.now(),
                session_status='active'
            )
            db.session.add(user_session)
            db.session.commit()

            # Store session in memory
            session_key = f"{new_game.game_id}_{user_id}"
            self.active_sessions[session_key] = {
                'game_id': new_game.game_id,
                'session_id': user_session.session_id,
                'user_id': user_id,
                'type': 'classic',
                'image_count': len(image_data),
                'selected_images': image_data,
                'status': 'active',
                'created_at': datetime.datetime.now(),
                'last_accessed': datetime.datetime.now()
            }

            print(f"Classic game initialized with {len(image_data)} images")
            return str(new_game.game_id), image_data

        except Exception as e:
            print(f"Error initializing classic game: {str(e)}")
            db.session.rollback()
            raise

    def join_game(self, game_id: int, user_id: str) -> Tuple[str, List[Dict]]:
        """
        Join an existing game
        """
        try:
            # Check if game exists and is active
            game = Game.query.filter_by(
                game_id=game_id, 
                game_status='active'
            ).first()
            
            if not game:
                raise ValueError(f"Game {game_id} not found or not active")

            if game.expiry_date and game.expiry_date < datetime.datetime.now():
                game.game_status = 'expired'
                db.session.commit()
                raise ValueError(f"Game {game_id} has expired")

            # Check if user already has an active session
            existing_session = UserGameSession.query.filter_by(
                game_id=game_id,
                user_id=user_id,
                session_status='active'
            ).first()

            if existing_session:
                raise ValueError(f"User already has an active session for game {game_id}")

            # Create new session for user
            user_session = UserGameSession(
                game_id=game_id,
                user_id=user_id,
                start_time=datetime.datetime.now(),
                session_status='active'
            )
            db.session.add(user_session)
            db.session.commit()

            # Get game images
            image_data = []
            for game_image in game.game_images:
                image = game_image.image
                image_data.append({
                    'url': f"/api/images/view/{image.image_path}",
                    'type': image.image_type
                })

            # Store session in memory
            session_key = f"{game_id}_{user_id}"
            self.active_sessions[session_key] = {
                'game_id': game_id,
                'session_id': user_session.session_id,
                'user_id': user_id,
                'type': 'classic',
                'image_count': len(image_data),
                'selected_images': image_data,
                'status': 'active',
                'created_at': datetime.datetime.now(),
                'last_accessed': datetime.datetime.now()
            }

            return str(game_id), image_data

        except Exception as e:
            print(f"Error joining game: {str(e)}")
            db.session.rollback()
            raise

    def finish_classic_game(self, game_id: str, user_id: str, user_guesses: List[Dict]) -> Dict:
        """
        Finish a classic game session for a user
        """
        try:
            session_key = f"{game_id}_{user_id}"
            session = self.active_sessions.get(session_key)
            
            if not session or session['status'] != 'active':
                raise ValueError(f"No active session found for user {user_id} in game {game_id}")

            # Get user session from database
            user_session = UserGameSession.query.filter_by(
                session_id=session['session_id']
            ).first()
            
            if not user_session:
                raise ValueError(f"Session not found in database")
            
            correct_guesses = 0
            total_guesses = len(user_guesses)
            
            # Record each guess
            for guess in user_guesses:
                image_url = guess.get('url')
                user_guess_type = guess.get('guess')
                
                # Find corresponding image
                game_image = next(
                    (img for img in session['selected_images'] if img['url'] == image_url),
                    None
                )
                
                if not game_image:
                    print(f"Warning: Image {image_url} not found in session")
                    continue
                    
                # Check if guess is correct
                is_correct = game_image['type'] == user_guess_type
                if is_correct:
                    correct_guesses += 1
                
                try:
                    # Get image_id from URL
                    image_path = image_url.split('/api/images/view/')[-1]
                    image = Images.query.filter_by(image_path=image_path).first()
                    
                    if image:
                        user_guess = UserGuess(
                            session_id=user_session.session_id,
                            image_id=image.image_id,
                            user_id=user_id,
                            user_guess_type=user_guess_type,
                            date_of_guess=datetime.datetime.now(),
                            is_correct=is_correct
                        )
                        db.session.add(user_guess)
                        db.session.commit()
                    
                except Exception as e:
                    print(f"Error recording guess: {str(e)}")
                    db.session.rollback()
            
            # Calculate score
            score = int((correct_guesses / total_guesses) * 100) if total_guesses > 0 else 0
            completion_time = datetime.datetime.now()
            time_taken = int((completion_time - user_session.start_time).total_seconds())
            
            # Update user session
            user_session.completion_time = completion_time
            user_session.session_status = 'completed'
            user_session.final_score = score
            user_session.correct_guesses = correct_guesses
            user_session.total_guesses = total_guesses
            user_session.time_taken = time_taken
            
            # Update user stats
            user = Users.query.filter_by(user_id=user_id).first()
            if user:
                user.score += score
                if score >= 70:  # Win condition: 70% or better
                    user.games_won += 1
            
            db.session.commit()
            
            # Update memory session
            session['status'] = 'completed'
            session['score'] = score
            session['correct_guesses'] = correct_guesses
            session['total_guesses'] = total_guesses
            
            return {
                'score': score,
                'correctGuesses': correct_guesses,
                'totalGuesses': total_guesses,
                'timeTaken': time_taken,
                'status': 'success'
            }
            
        except Exception as e:
            print(f"Error finishing classic game: {str(e)}")
            db.session.rollback()
            raise

    def get_session(self, game_id: str, user_id: str) -> Dict:
        """Get game session data for a specific user"""
        session_key = f"{game_id}_{user_id}"
        session = self.active_sessions.get(session_key)
        if not session:
            raise ValueError(f"Session not found for user {user_id} in game {game_id}")
        session['last_accessed'] = datetime.datetime.now()
        return session