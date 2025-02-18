
from __init__ import db
from models import *
from sqlalchemy import text, bindparam, func
from datetime import datetime 
import os
from flask import jsonify, flash
from werkzeug.utils import secure_filename
from decimal import Decimal


def get_users_with_filters(sort_by=None, sort_order='asc', limit=20, offset=0, level=None, min_games_won=None, max_games_won=None, min_score=None, max_score=None):
    try:
        # Start the query string
        query_str = """
            SELECT * FROM users
            WHERE 1=1
        """

        # Dictionary to store query parameters
        params = {'limit': limit, 'offset': offset}

        # Apply filters conditionally

        if level is not None:
            query_str += " AND level = :level"
            params['level'] = level

        if min_games_won is not None:
            query_str += " AND games_won >= :min_games_won"
            params['min_games_won'] = min_games_won

        if max_games_won is not None:
            query_str += " AND games_won <= :max_games_won"
            params['max_games_won'] = max_games_won

        if min_score is not None:
            query_str += " AND score >= :min_score"
            params['min_score'] = min_score

        if max_score is not None:
            query_str += " AND score <= :max_score"
            params['max_score'] = max_score

        # Define valid sorting fields
        valid_sort_fields = ['user_id', 'username', 'level', 'games_won', 'score']
        
        # Apply sorting if a valid sort_by field is provided
        if sort_by in valid_sort_fields:
            query_str += f" ORDER BY {sort_by} {sort_order.upper()}"
        else:
            query_str += " ORDER BY user_id ASC"  # Default sorting by user_id

        # Add LIMIT and OFFSET for pagination
        query_str += " LIMIT :limit OFFSET :offset"

        # Execute the query
        query = text(query_str)
        result = db.session.execute(query, params)

        # Process and format the results
        users_data = []
        for row in result.mappings():
            users_data.append({
                'user_id': row['user_id'],
                'username': row['username'],
                'level': row['level'],
                'games_won': row['games_won'],
                'score': row['score']
            })

        return users_data
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []




def get_users_ordered():
    try:
        query = text("""
            SELECT 
                user_id, username, level, exp, games_started, games_won, score
            FROM users
            ORDER BY user_id;
        """)
        result = db.session.execute(query)
        db.session.commit()

        users = []
        for row in result:
            users.append({column: value for column, value in zip(result.keys(), row)})

        return users

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}