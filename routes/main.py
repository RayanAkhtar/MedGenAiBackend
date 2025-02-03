import uuid
from datetime import datetime, timezone

from flask import jsonify, request
from __init__ import db
from sqlalchemy import text
from . import bp
from models import *

@bp.route('/hello')
def hello():
    return jsonify(message="Hello, world!"), 200

@bp.route('/execute_sql', methods=['POST'])
def execute_sql():
    try:
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        sql_query = json_data.get('query')
        if not sql_query:
            return jsonify({"error": "No SQL query provided"}), 400

        query = text(sql_query)
        result = db.session.execute(query)
        db.session.commit()

        if result.returns_rows:
            rows = []
            for row in result:
                row_dict = {column: value for column, value in zip(result.keys(), row)}
                rows.append(row_dict)
            return jsonify(rows)

        return jsonify({"message": "Query executed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "details": str(e)}), 400

@bp.route('/user-response', methods = ['POST', 'GET'])
def process_response():
  if request.method == 'GET':
    return jsonify({"message": "Endpoint is working!"}), 200
  try:
    # Parse JSON payload
    data = request.json
    imageID = data['imageID']
    userID = data['userID']
    user_guess_type = data['user_guess_type']
    x = data['x']
    y = data['y']
    feedback_text = data['feedback']

    # Produce extra data needed for tables
    timestamp = datetime.now(timezone.utc)
    guessID = str(uuid.uuid4())
    feedbackID = str(uuid.uuid4())

    # Insert into UserGuess table
    user_guess = UserGuess(
      guess_id=guessID,
      image_id=imageID,
      user_id=userID,
      user_guess_type=user_guess_type,
      date_of_guess=timestamp
    )
    db.session.add(user_guess)

    # Insert into Feedback table
    feedback = Feedback(
      feedback_id=feedbackID,
      x=x,
      y=y,
      msg=feedback_text
      # resolved is false by default
    )
    db.session.add(feedback)

    # Insert into FeedbackUser table
    feedback_user = FeedbackUser(
      feedback_id=feedbackID,
      guess_id=guessID
    )
    db.session.add(feedback_user)

    db.session.commit()
    return jsonify({"message": "Response submitted successfully."}), 200

  except Exception as e:
    db.session.rollback()
    return jsonify({"error": str(e)}), 500