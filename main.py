import logging
import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from flask_cors import CORS

# Uncomment when debugging
# logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medgen.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Competition(db.Model):
    __tablename__ = 'competitions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

class CompetitionUser(db.Model):
    __tablename__ = 'competition_users'

    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)

    competition = db.relationship('competition', backref=db.backref('users', lazy=True))

# Creates database and tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/execute_sql', methods=['POST'])
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

    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback the session if there's a DB error
        logging.error(f"SQLAlchemy Error: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 400

    except Exception as e:
        logging.error(f"General Error: {str(e)}")
        return jsonify({"error": "An error occurred", "details": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5328)
