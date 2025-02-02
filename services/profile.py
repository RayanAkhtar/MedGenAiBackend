def get_profile_data(user_id):
    """
    Get basic profile information for a user
    Args:
        user_id: ID of the user to get profile for
    Returns:
        dict: A dictionary containing user profile statistics including:
            - gamesPlayed (int): Total number of games played
            - accuracy (float): Average accuracy percentage 
            - streak (int): Current winning streak
            - rank (int): Global ranking
            - points (int): Total points earned
            - badges (int): Number of badges earned
    """
    # TODO: Implement database queries to populate stats
    pass

def get_recent_game_history(user_id):
    """
    Get recent game history for a user
    Args:
        user_id: ID of the user to get history for
    Returns:
        dict: A list of dictionaries containing recent game data including:
            - id (int): Game ID
            - type (str): Game type (Classic, Competitive, Special)
            - score (int): Score achieved
            - date (str): Date played
            - images (int): Number of images in game
    """
    # TODO: Implement database queries to get recent games
    pass

def get_user_performance(user_id):
    """
    Get performance statistics for a user
    Args:
        user_id: ID of the user to get stats for
    Returns:
        dict: A dictionary containing performance data for different game modes:
            - all (dict): Overall performance data with labels and scores
            - classic (dict): Classic mode performance data
            - competitive (dict): Competitive mode performance data
            - special (dict): Special mode performance data
            Each mode contains:
                - labels (list): Date labels
                - data (list): Corresponding scores
    """
    # TODO: Implement database queries to get performance stats to be used to populate a chart
    pass

def get_user_badges(user_id):
    """
    Get badges earned by a user
    Args:
        user_id: ID of the user to get badges for
    Returns:
        dict: A list of dictionaries containing badge information:
            - id (int): Badge ID
            - name (str): Badge name
            - icon (str): Badge icon emoji
            - description (str): Badge description
            - date (str): Date earned
    """
    # TODO: Implement database queries to get badges to be used to populate a badge list
    pass
