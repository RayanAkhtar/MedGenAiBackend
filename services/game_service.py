from models import Users, Images, UserGuess, Game, GameImages, UserGameSession, Feedback, FeedbackUser
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

            # Calculate how many of each type to fetch
            real_count = image_count // 2
            ai_count = image_count // 2
            
            # If odd number, add one more real image
            if image_count % 2 != 0:
                real_count += 1
            
            print(f"Fetching {real_count} real images and {ai_count} AI images")
            
            real_images = get_images_rand(real_count, 'real')
            print(f"Got {len(real_images)} real images")
            
            ai_images = get_images_rand(ai_count, 'ai')
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

            # Check if user already has a session for this game (active or completed)
            existing_session = UserGameSession.query.filter_by(
                game_id=game_id,
                user_id=user_id
            ).first()

            if existing_session:
                if existing_session.session_status == 'active':
                    raise ValueError(f"User already has an active session for game {game_id}")
                else:
                    raise ValueError(f"User has already played game {game_id}")

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

    def finish_classic_game(self, game_id, user_id, user_guesses):
        """
        Finish a classic game and update user's score
        
        Args:
            game_id (str): ID of the game
            user_id (str): ID of the user
            user_guesses (list): List of user guesses with format:
                [
                    {
                        "url": str,
                        "guess": str,
                        "feedback": str (optional),
                        "x": float (optional),
                        "y": float (optional)
                    },
                    ...
                ]
        
        Returns:
            dict: Game results including score and stats
        """
        try:
            from datetime import datetime
            
            print(f"Processing game completion for user {user_id}, game {game_id}")
            print(f"Received {len(user_guesses)} guesses")
            
            # Get the user
            user = Users.query.filter_by(user_id=user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Get the game
            game = Game.query.filter_by(game_id=game_id).first()
            if not game:
                raise ValueError("Game not found")
            
            # Create or get user game session
            session = UserGameSession.query.filter_by(
                game_id=game_id,
                user_id=user_id
            ).first()
            
            if not session:
                # Create new session
                session = UserGameSession(
                    game_id=game_id,
                    user_id=user_id,
                    start_time=datetime.now(),
                    session_status="completed"
                )
                db.session.add(session)
                db.session.flush()  # Get the session ID
            
            # Process user guesses
            correct_guesses = 0
            total_guesses = 0
            
            for guess_data in user_guesses:
                # Extract data from the new format
                image_url = guess_data.get('url')
                user_guess_type = guess_data.get('guess')
                feedback_text = guess_data.get('feedback')
                x_coord = guess_data.get('x')
                y_coord = guess_data.get('y')
                
                # Skip if missing essential data
                if not image_url or not user_guess_type:
                    print(f"Warning: Skipping invalid guess with url={image_url}, guess={user_guess_type}")
                    continue
                
                # Extract image_path from URL
                # URL format: http://127.0.0.1:5328/api/images/view//path/to/image.jpg
                image_path = image_url.split('/api/images/view/')[-1]
                
                # Clean up the path - remove leading slashes
                while image_path.startswith('/'):
                    image_path = image_path[1:]
                
                print(f"Looking for image with path: {image_path}")
                
                # Try to find the image with exact path
                image = Images.query.filter_by(image_path=image_path).first()
                
                # If not found, try with a leading slash
                if not image:
                    image = Images.query.filter_by(image_path=f"/{image_path}").first()
                
                # If still not found, try with the filename only
                if not image:
                    filename = image_path.split('/')[-1]
                    image = Images.query.filter(Images.image_path.like(f'%{filename}')).first()
                
                if not image:
                    print(f"Warning: Image with path '{image_path}' not found in database")
                    continue
                
                # Check if guess is correct
                is_correct = (user_guess_type == image.image_type)
                if is_correct:
                    correct_guesses += 1
                total_guesses += 1
                
                # Save the guess without is_correct field
                user_guess = UserGuess(
                    user_id=user_id,
                    image_id=image.image_id,
                    user_guess_type=user_guess_type,
                    time_taken=0,  # No time data in current format
                    session_id=session.session_id,
                    date_of_guess=datetime.now()
                )
                db.session.add(user_guess)
                db.session.flush()  # Get the guess ID
                
                # Process feedback if provided
                if feedback_text or (x_coord is not None and y_coord is not None):
                    # Create feedback entry
                    feedback = Feedback(
                        x=x_coord if x_coord is not None else 0,
                        y=y_coord if y_coord is not None else 0,
                        msg=feedback_text if feedback_text else "",
                        resolved=False,
                        date_added=datetime.now(),
                        confidence=50  # Default confidence value
                    )
                    db.session.add(feedback)
                    db.session.flush()  # Get the feedback ID
                    
                    # Link feedback to user guess
                    feedback_user = FeedbackUser(
                        feedback_id=feedback.feedback_id,
                        guess_id=user_guess.guess_id
                    )
                    db.session.add(feedback_user)
            
            # Calculate score - 10 points per correct guess
            score = correct_guesses * 10
            
            # Update session
            session.completion_time = datetime.now()
            session.final_score = score
            session.correct_guesses = correct_guesses
            session.total_guesses = total_guesses
            session.session_status = "completed"
            
            # Update user stats
            user.score += score
            if correct_guesses > 0:
                user.games_won += 1
            
            # Commit changes
            db.session.commit()
            
            print(f"Game completed successfully. Score: {score}, Correct: {correct_guesses}, Total: {total_guesses}")
            
            # Return results
            return {
                'score': score,
                'correctGuesses': correct_guesses,
                'totalGuesses': total_guesses,
                'status': 'success'
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"Error in finish_classic_game: {str(e)}")
            raise

    def get_session(self, game_id: str, user_id: str) -> Dict:
        """Get game session data for a specific user"""
        session_key = f"{game_id}_{user_id}"
        session = self.active_sessions.get(session_key)
        if not session:
            raise ValueError(f"Session not found for user {user_id} in game {game_id}")
        session['last_accessed'] = datetime.datetime.now()
        return session
    

    def get_game(self, game_id: str, user_id: str = None) -> Dict:
        """
        Get game data including images and sessions
        
        Args:
            game_id (str): ID of the game to retrieve
            user_id (str, optional): If provided, also returns this user's session data
            
        Returns:
            dict: Game data including images and sessions
        """
        try:
            # Get the game
            game = Game.query.filter_by(game_id=game_id).first()
            if not game:
                raise ValueError(f"Game with ID {game_id} not found")
            
            # Get all game images
            game_images = []
            for game_image in game.game_images:
                image = game_image.image
                game_images.append({
                    'url': f"/api/images/view/{image.image_path}",
                    'type': image.image_type
                })
            
            # Get all sessions for this game
            sessions = []
            for session in UserGameSession.query.filter_by(game_id=game_id).all():
                user = Users.query.filter_by(user_id=session.user_id).first()
                
                session_data = {
                    'session_id': session.session_id,
                    'user_id': session.user_id,
                    'username': user.username if user else "Unknown",
                    'start_time': session.start_time.isoformat() if session.start_time else None,
                    'completion_time': session.completion_time.isoformat() if session.completion_time else None,
                    'status': session.session_status,
                    'score': session.final_score
                }
                
                sessions.append(session_data)
            
            # Build response
            response = {
                'game_id': game.game_id,
                'images': game_images,
            }
        
            return response
            
        except Exception as e:
            print(f"Error in get_game: {str(e)}")
            raise
        