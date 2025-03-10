from models import Users, Images, UserGuess, Game, GameImages, UserGameSession, Feedback, FeedbackUser, Competition, CompetitionGame, GameCode
from __init__ import db
from typing import Tuple, List, Dict
import uuid
import datetime
import random
from services.images import get_images_rand

class GameService:
    def __init__(self):
        print("Initializing GameService")
        self.active_sessions = {}

    def initialize_classic_game(self, image_count: int, user_id: str) -> Tuple[str, List[Dict], str]:
        """
        Initialize a classic game with mixed real and AI images
        
        Args:
            image_count (int): Total number of images for the game
            user_id (str): User's ID who is creating the game
            
        Returns:
            Tuple[str, List[dict], string]: Game ID, list of image URLs, and game code
        """
        try:
            print(f"[DEBUG] Initializing classic game for user {user_id}")
            print(f"[DEBUG] Requested image count: {image_count}")

            # Calculate how many of each type to fetch
            real_count = image_count // 2
            ai_count = image_count // 2
            
            # If odd number, add one more real image
            if image_count % 2 != 0:
                real_count += 1
                print(f"[DEBUG] Odd number of images, adding extra real image. Real: {real_count}, AI: {ai_count}")
            
            print(f"[DEBUG] Fetching {real_count} real images and {ai_count} AI images")
            
            real_images = get_images_rand(real_count, 'real')
            print(f"[DEBUG] Got {len(real_images)} real images")
            print(f"[DEBUG] Real image URLs: {real_images}")
            
            ai_images = get_images_rand(ai_count, 'ai')
            print(f"[DEBUG] Got {len(ai_images)} AI images")
            print(f"[DEBUG] AI image URLs: {ai_images}")

            print("[DEBUG] Creating new game in database")
            # Create new game in database
            
            new_game = Game(
                game_mode='classic',
                date_created=datetime.datetime.now(),
                game_board='classic',
                game_status='active',
                expiry_date=datetime.datetime.now() + datetime.timedelta(days=1),  # Game expires in 24 hours
                created_by=user_id,
            )
            db.session.add(new_game)
            db.session.flush()  # This will show errors before commit
            print(f"Game created successfully with ID: {new_game.game_id}")

            # Generate a unique game code
            game_code = str(uuid.uuid4())[:8].upper()
            # Create GameCodeTable entry
            game_code_entry = GameCode(
                game_id=new_game.game_id,
                game_code=game_code
            )
            # print in red
            print(f"\033[91m[DEBUG] Game code: {game_code}\033[0m")
            db.session.add(game_code_entry)
            
            # Format images with their types and create GameImages entries
            image_data = []
            print("[DEBUG] Processing images and creating GameImages entries")
            for url in real_images + ai_images:
                print(f"[DEBUG] Processing image URL: {url}")
                # Get image_id from URL
                image_path = url.split('/api/images/view/')[-1]
                print(f"[DEBUG] Extracted image path: {image_path}")
                image = Images.query.filter_by(image_path=image_path).first()
                
                if image:
                    print(f"[DEBUG] Found image in database with ID: {image.image_id}")
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
                    print(f"[DEBUG] Added image to game: {url} (type: {image.image_type})")
                else:
                    print(f"[WARNING] Image not found in database: {image_path}")

            print("[DEBUG] Creating initial game session for creator")
            # Create initial game session for creator
            user_session = UserGameSession(
                game_id=new_game.game_id,
                user_id=user_id,
                start_time=datetime.datetime.now(),
                session_status='active'
            )
            db.session.add(user_session)
            db.session.commit()
            print(f"[DEBUG] Created user session with ID: {user_session.session_id}")

            # Store session in memory
            session_key = f"{new_game.game_id}_{user_id}"
            print(f"[DEBUG] Storing session in memory with key: {session_key}")
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

            print(f"[DEBUG] Classic game initialized successfully with {len(image_data)} images")
            return str(new_game.game_id), image_data, game_code

        except Exception as e:
            print(f"[ERROR] Error initializing classic game: {str(e)}")
            print(f"[ERROR] Stack trace:", exc_info=True)
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
            print(f"User session: {user_session}")
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
        """
        try:
            print(f"Starting game completion for user {user_id}, game {game_id}")
            
            # Get the user and game
            user = Users.query.filter_by(user_id=user_id).first()
            game = Game.query.filter_by(game_id=game_id).first()
            
            if not user or not game:
                raise ValueError("User or game not found")
            
            # Get existing session or create new one
            session = UserGameSession.query.filter_by(
                game_id=game_id,
                user_id=user_id,
            ).first()
            
            start_time = datetime.datetime.now()
            if not session:
                print(f"Creating new game session for user {user_id}")
                session = UserGameSession(
                    game_id=game_id,
                    user_id=user_id,
                    start_time=start_time,
                    session_status='active'
                )
                db.session.add(session)
                db.session.flush()
            else:
                start_time = session.start_time or start_time
                print(f"Found existing session {session.session_id}")
            
            # Process guesses and calculate score
            correct_guesses = 0
            total_guesses = len(user_guesses)
            
            for guess in user_guesses:
                image_path = guess['url'].split('/api/images/view/')[-1]
                image = Images.query.filter_by(image_path=image_path).first()
                
                if image and guess['guess'] == image.image_type:
                    correct_guesses += 1
            
            # Calculate metrics
            current_time = datetime.datetime.now()
            accuracy = (correct_guesses / total_guesses * 100) if total_guesses > 0 else 0
            score = correct_guesses * 10
            time_taken = (current_time - start_time).total_seconds()
            
            print(f"Updating session {session.session_id} with completion data")
            # Update session with completion data
            session.completion_time = current_time
            session.final_score = score
            session.correct_guesses = correct_guesses
            session.total_guesses = total_guesses
            session.session_status = 'completed'
            session.accuracy = accuracy
            session.time_taken = time_taken
            
            # Update user stats
            user.score = (user.score or 0) + score
            user.games_won = (user.games_won or 0) + (1 if correct_guesses > 0 else 0)
            user.games_started = (user.games_started or 0) + 1
            
            print(f"Game session data:")
            print(f"Session ID: {session.session_id}")
            print(f"Start Time: {session.start_time}")
            print(f"Completion Time: {session.completion_time}")
            print(f"Score: {session.final_score}")
            print(f"Correct Guesses: {session.correct_guesses}/{session.total_guesses}")
            print(f"Accuracy: {session.accuracy:.2f}%")
            print(f"Time Taken: {session.time_taken} seconds")
            print(f"Status: {session.session_status}")
            
            # Commit all changes
            db.session.commit()
            print(f"Successfully saved game session {session.session_id}")
            
            return {
                'score': score,
                'correctGuesses': correct_guesses,
                'totalGuesses': total_guesses,
                'accuracy': accuracy,
                'completionTime': current_time.isoformat(),
                'timeTaken': time_taken,
                'sessionId': session.session_id,
                'status': 'success'
            }
            
        except Exception as e:
            print(f"Error in finish_classic_game: {str(e)}")
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
            print(f"Getting game with ID {game_id} for user {user_id}")
            game_code_obj = GameCode.query.filter_by(game_code=game_id).first()
            if game_code_obj:
                game_id = game_code_obj.game_id
            # Get the game
            game = Game.query.filter_by(game_id=game_id).first()
            print(f"Found game: {game}")
            if not game:
                raise ValueError(f"Game with ID {game_id} not found")
            
            # Get all game images
            game_images = []
            print(f"Getting images for game {game_id}")
            for game_image in game.game_images:
                image = game_image.image
                print(f"Processing image {image.image_id}: {image.image_path}")
                game_images.append({
                    'url': f"/api/images/view/{image.image_path}",
                    'type': image.image_type
                })
            print(f"Found {len(game_images)} images")
            
            # Get all sessions for this game
            sessions = []
            print(f"Getting sessions for game {game_id}")
            # get game id from game code
            # Check if game_id is actually a game code
            
            print(f"Game ID: {game_id}")
            for session in UserGameSession.query.filter_by(game_id=game_id).all():
                user = Users.query.filter_by(user_id=session.user_id).first()
                print(f"Processing session {session.session_id} for user {user.username if user else 'Unknown'}")
                
                session_data = {
                    'session_id': session.session_id,
                    'user_id': session.user_id,
                    'username': user.username if user else "Unknown",
                    'start_time': session.start_time.isoformat() if session.start_time else None,
                    'completion_time': session.completion_time.isoformat() if session.completion_time else None,
                    'status': session.session_status,
                    'score': session.final_score
                }
                print(f"Session data: {session_data}")
                
                sessions.append(session_data)
            print(f"Found {len(sessions)} sessions")
            
            # Build response
            response = {
                'game_id': game.game_id,
                'images': game_images,
            }
            print(f"Returning response for game {game_id}")
        
            return response
            
        except Exception as e:
            print(f"Error in get_game: {str(e)}")
            raise

    def initialize_game_with_code(self, game_code: str, user_id: str, image_count: int) -> Tuple[str, List[Dict], str]:
        """
        Initialize a game with a specified game code
        
        Args:
            game_code (str): Code of the game to initialize
            user_id (str): ID of the user
            
        Returns:
            Tuple[str, List[Dict]]: Game ID and list of images
            
        Raises:
            ValueError: If game not found, expired, or user already completed it
        """
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
        # Check if game code exists
        check_game_code = Game.query.filter_by(game_id=int(game_code)).first()
        if check_game_code:
            # return error
            raise ValueError("Game code already exists")
        
        # Create new game
        new_game = Game(
            game_id=int(game_code),
            game_mode='custom',
            date_created=datetime.datetime.now(),
            game_board='single',
            game_status='active',
            expiry_date=datetime.datetime.now() + datetime.timedelta(days=1),
            created_by=user_id
        )
        db.session.add(new_game)
        db.session.flush()
        # Create GameCode entry
        game_code_entry = GameCode(
            game_id=new_game.game_id,
            game_code=game_code
        )
        db.session.add(game_code_entry)
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
        return str(new_game.game_id), image_data, game_code
    def get_random_competition_game(self, user_id: str) -> Tuple[str, List[Dict]]:
        """
        Get a random game from all available games that hasn't expired
        
        Args:
            user_id (str): ID of the user
            
        Returns:
            Tuple[str, List[Dict]]: Game ID and list of image URLs
        """
        try:
            print(f"Getting random game for user {user_id}")
            
            # Get a random game that is active and not expired
            game = Game.query.filter(
                Game.game_status == 'active',
                (Game.expiry_date > datetime.datetime.now()) | (Game.expiry_date.is_(None))
            ).order_by(db.func.random()).first()
            
            if not game:
                raise ValueError("No active non-expired games found")
            
            print(f"Found game ID: {game.game_id}")
            
            # Use the join_game method to get the game details
            return self.join_game(game.game_id, user_id)
            
        except Exception as e:
            print(f"Error getting random game: {str(e)}")
            raise
