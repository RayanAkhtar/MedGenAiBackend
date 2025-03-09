from models import Users, UserGameSession, Game, Images, GameImages
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from __init__ import db

def get_profile_data(user_id):
    """
    Get basic profile information for a user
    Args:
        user_id: ID of the user to get profile for
    Returns:
        dict: A dictionary containing user profile statistics including:
            - gamesPlayed (int): Total number of games played
            - accuracy (float): Average accuracy percentage 
            - rank (int): Global ranking
            - points (int): Total points earned
    """
    # Get user from database
    user = Users.query.filter_by(user_id=user_id).first()
    if not user:
        raise ValueError(f"User with ID {user_id} not found")
    
    # Get completed game sessions
    completed_sessions = UserGameSession.query.filter_by(
        user_id=user_id,
    ).all()
    
    # Calculate total games played
    games_played = len(completed_sessions)
    
    # Calculate accuracy
    total_correct = sum(session.correct_guesses or 0 for session in completed_sessions)
    total_guesses = sum(session.total_guesses or 0 for session in completed_sessions)
    
    accuracy = 0
    if total_guesses > 0:
        accuracy = round((total_correct / total_guesses) * 100, 1)
    
    # Calculate user rank
    user_rank = Users.query.filter(Users.score > user.score).count() + 1
    
    # Get total points
    points = user.score or 0
    
    print(f"Profile data for user {user_id}:")
    print(f"Games played: {games_played}")
    print(f"Total correct: {total_correct}")
    print(f"Total guesses: {total_guesses}")
    print(f"Accuracy: {accuracy}%")
    print(f"Rank: {user_rank}")
    print(f"Points: {points}")
    
    return {
        "gamesPlayed": games_played,
        "accuracy": accuracy,
        "rank": user_rank,
        "points": points
    }

def get_recent_game_history(user_id):
    """
    Get recent game history for a user
    Args:
        user_id: ID of the user to get history for
    Returns:
        list: A list of dictionaries containing recent game data including:
            - id (int): Game ID
            - type (str): Game type (Classic, Competitive, Special) 
            - accuracy (float): Accuracy percentage achieved
            - date (str): Date played
            - images (int): Number of images in game
    """
    # Get user's completed game sessions, ordered by completion time
    sessions = UserGameSession.query.filter_by(
        user_id=user_id,
        session_status='completed'  # Only get completed sessions
    ).order_by(UserGameSession.completion_time.desc()).limit(10).all()
    
    print(f"Found {len(sessions)} recent games for user {user_id}")
    
    history = []
    for session in sessions:
        # Get game details
        game = Game.query.filter_by(game_id=session.game_id).first()
        if not game:
            continue
            
        # Count images in game
        image_count = db.session.query(func.count(Images.image_id)).join(
            GameImages, GameImages.image_id == Images.image_id
        ).filter(
            GameImages.game_id == game.game_id
        ).scalar() or 0
        
        # Format date
        date_played = session.completion_time.strftime("%Y-%m-%d %H:%M") if session.completion_time else "Unknown"
        
        # Calculate accuracy
        accuracy = 0
        if session.total_guesses and session.total_guesses > 0:
            accuracy = round((session.correct_guesses / session.total_guesses) * 100, 1)
        
        game_data = {
            "id": session.game_id,
            "type": game.game_mode.capitalize(),
            "accuracy": accuracy,
            "date": date_played,
            "images": image_count,
            "score": session.final_score,
            "correctGuesses": session.correct_guesses,
            "totalGuesses": session.total_guesses
        }
        
        print(f"Game data: {game_data}")
        history.append(game_data)
    
    return {"games": history}

def get_user_performance(user_id):
    """
    Get performance statistics for a user over time
    Args:
        user_id: ID of the user to get stats for
    Returns:
        dict: A dictionary containing performance data for different game modes:
            - all (dict): Overall performance data with labels and accuracy
            - single (dict): single mode performance data  
            - dual (dict): dual mode performance data
            Each mode contains:
                - labels (list): Date labels
                - data (list): Corresponding accuracy percentages
    """
    # Get user's completed game sessions from the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    sessions = UserGameSession.query.filter(
        UserGameSession.user_id == user_id,
        UserGameSession.session_status == 'completed',
        UserGameSession.completion_time >= thirty_days_ago
    ).order_by(UserGameSession.completion_time).all()
    
    print(f"Found {len(sessions)} sessions in last 30 days for user {user_id}")
    
    # Initialize performance data
    all_mode = {"labels": [], "data": []}
    single_mode = {"labels": [], "data": []}
    dual_mode = {"labels": [], "data": []}
    
    for session in sessions:
        # Get game details
        game = Game.query.filter_by(game_id=session.game_id).first()
        if not game or not session.completion_time:
            continue
            
        # Format date label
        date_label = session.completion_time.strftime("%m/%d")
        
        # Calculate accuracy percentage
        accuracy = 0
        if session.total_guesses and session.total_guesses > 0:
            accuracy = round((session.correct_guesses / session.total_guesses) * 100, 1)
        
        print(f"Session {session.session_id}: {accuracy}% accuracy on {date_label}")
        
        # Add to all modes
        all_mode["labels"].append(date_label)
        all_mode["data"].append(accuracy)
        
        # Add to specific mode
        if game.game_mode.lower() == "single":
            single_mode["labels"].append(date_label)
            single_mode["data"].append(accuracy)
        elif game.game_mode.lower() == "dual":
            dual_mode["labels"].append(date_label)
            dual_mode["data"].append(accuracy)
    
    return {
        "all": all_mode,
        "single": single_mode,
        "dual": dual_mode
    }

