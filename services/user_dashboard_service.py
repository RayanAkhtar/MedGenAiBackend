from models import Users, UserGameSession, UserGuess, Game
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from flask import current_app
import math

class UserDashboardService:
    def get_user_stats(self, user_id):
        """Get user statistics for the dashboard"""
        # Get user from database
        user = Users.query.filter_by(user_id=user_id).first()
        if not user:
            raise ValueError("User not found")
            
        # Calculate average accuracy
        accuracy_query = UserGuess.query.filter_by(user_id=user_id)
        total_guesses = accuracy_query.count()
        
        if total_guesses > 0:
            correct_guesses = accuracy_query.filter_by(is_correct=True).count()
            average_accuracy = round((correct_guesses / total_guesses) * 100)
        else:
            average_accuracy = 0
            
        # Count completed challenges/games
        challenges_completed = UserGameSession.query.filter_by(
            user_id=user_id,
            session_status="completed"
        ).count()
        
        # Calculate user rank based on score
        user_rank_query = Users.query.filter(Users.score > user.score).count()
        current_rank = user_rank_query + 1  # Add 1 because ranks start at 1
        
        return {
            "averageAccuracy": average_accuracy,
            "challengesCompleted": challenges_completed,
            "currentRank": current_rank
        }
    
    def get_recent_activity(self, user_id):
        """Get user's recent game activity"""
        # Get recent sessions for this user
        recent_sessions = UserGameSession.query.filter_by(user_id=user_id)\
            .order_by(UserGameSession.completion_time.desc())\
            .limit(5)\
            .all()
            
        activities = []
        
        for session in recent_sessions:
            # Skip incomplete sessions
            if session.completion_time is None:
                continue
                
            # Get game details
            game = Game.query.filter_by(game_id=session.game_id).first()
            if not game:
                continue
                
            # Calculate accuracy for this session
            if session.total_guesses and session.total_guesses > 0:
                accuracy = round((session.correct_guesses / session.total_guesses) * 100)
            else:
                accuracy = 0
                
            # Format date
            date_str = session.completion_time.strftime("%b %d, %Y")
            
            # Get image count for this game
            image_count = session.total_guesses if session.total_guesses else 0
            
            activities.append({
                "gameType": game.game_mode.capitalize(),
                "imageCount": image_count,
                "accuracy": accuracy,
                "date": date_str
            })
            
        return {
            "activities": activities
        }
    
    def get_leaderboard(self):
        """Get global leaderboard data"""
        # Get top 10 users by score
        top_users = Users.query.order_by(Users.score.desc()).limit(10).all()
        
        players = []
        
        for rank, user in enumerate(top_users, 1):
            # Calculate user's accuracy
            user_guesses = UserGuess.query.filter_by(user_id=user.user_id)
            total_guesses = user_guesses.count()
            
            if total_guesses > 0:
                correct_guesses = user_guesses.filter_by(is_correct=True).count()
                accuracy = round((correct_guesses / total_guesses) * 100)
            else:
                accuracy = 0
                
            # Get username or use email as fallback
            display_name = user.username if user.username else user.email
            
            # Truncate long names
            if display_name and len(display_name) > 20:
                display_name = display_name[:17] + "..."
                
            players.append({
                "rank": rank,
                "name": display_name,
                "accuracy": accuracy
            })
            
        return {
            "players": players
        }
