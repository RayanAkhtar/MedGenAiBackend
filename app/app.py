from flask import Blueprint, jsonify, request
from sqlalchemy import text
from . import db  # Import the database object from __init__.py

bp = Blueprint('main', __name__)

@bp.route('/')
def hello():
    return jsonify(message="Hello, world!")

@bp.route('/execute_sql', methods=['POST'])
def execute_sql():
    try:
        sql_query = request.json.get('query')
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

        return jsonify({"message": "Query executed successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "details": str(e)}), 400
