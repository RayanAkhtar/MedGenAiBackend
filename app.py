import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy  
from flask_cors import CORS
from sqlalchemy import text 
import json


db = SQLAlchemy()  


app = Flask(__name__)

CORS(app)


app.config.from_mapping(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///medgen.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db.init_app(app)

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


@app.route('/hello')
def hello():
    return jsonify(message="Hello, world!"), 200

@app.route('/execute_sql', methods=['POST'])
def execute_sql():
    try:
        data = request.get_data(as_text=True)
        json_data = json.loads(data) if data else {}
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5328)))
