from models import Users, UserGameSession, UserGuess, Game
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from flask import current_app
import math
from __init__ import db
class UserDashboardService:
    def get_user_stats(self, user_id):
        """Get user statistics for the dashboard"""
        # Get user from database
        user = Users.query.filter_by(user_id=user_id).first()
        if not user:
            raise ValueError("User not found")
            
        # Calculate average accuracy from completed game sessions
        completed_sessions = UserGameSession.query.filter_by(
            user_id=user_id,
            session_status="completed"
        ).all()
        
        total_correct = 0
        total_guesses = 0
        
        for session in completed_sessions:
            total_correct += session.correct_guesses or 0
            total_guesses += session.total_guesses or 0
        
        if total_guesses > 0:
            average_accuracy = round((total_correct / total_guesses) * 100)
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
            # Calculate user's accuracy based on game sessions
            user_sessions = UserGameSession.query.filter_by(
                user_id=user.user_id, 
                session_status="completed"
            )
            total_sessions = user_sessions.count()
            
            if total_sessions > 0:
                # Get sum of correct guesses and total guesses from all sessions
                session_stats = db.session.query(
                    func.sum(UserGameSession.correct_guesses).label("total_correct"),
                    func.sum(UserGameSession.total_guesses).label("total_guesses")
                ).filter(
                    UserGameSession.user_id == user.user_id,
                    UserGameSession.session_status == "completed"
                ).first()
                
                total_correct = session_stats.total_correct or 0
                total_guesses = session_stats.total_guesses or 0
                
                if total_guesses > 0:
                    accuracy = round((total_correct / total_guesses) * 100)
                else:
                    accuracy = 0
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
