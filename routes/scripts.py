from flask import Blueprint, jsonify
from services.scripts import drop_tables, setup_tables, populate_tables

bp = Blueprint('scripts', __name__)

@bp.route('/scripts/dropTables', methods=['POST'])
def drop_tables_route():
    try:
        drop_tables()
        return jsonify({"message": "Tables dropped successfully."}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred while dropping tables: {str(e)}"}), 500

@bp.route('/scripts/setupTables', methods=['POST'])
def setup_tables_route():
    try:
        setup_tables()
        return jsonify({"message": "Tables setup successfully."}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred while setting up tables: {str(e)}"}), 500

@bp.route('/scripts/populateTables', methods=['POST'])
def populate_tables_route():
    try:
        populate_tables()
        return jsonify({"message": "Tables populated successfully."}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred while populating tables: {str(e)}"}), 500
