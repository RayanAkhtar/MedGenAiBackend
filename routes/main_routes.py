from flask import jsonify, request
from .. import db
from sqlalchemy import text

def init_app(app):
    @app.route('/hello')
    def hello():
        return jsonify(message="Hello, world!"), 200

    @app.route('/execute_sql', methods=['POST'])
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