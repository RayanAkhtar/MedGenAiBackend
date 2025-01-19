import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text

# Initialize the database object
db = SQLAlchemy()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all domains (you can restrict it later as needed)
CORS(app)

# Load configuration
app.config.from_mapping(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///medgen.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

# Initialize the database with the app
db.init_app(app)

# Define the routes directly on the app object
@app.route('/hello')
def hello():
    return jsonify(message="Hello, world!"), 200

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

        return jsonify({"message": "Query executed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "details": str(e)}), 400

# If this is the main module, run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5328)))
