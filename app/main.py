from flask import Blueprint, jsonify

# Create a blueprint instance
bp = Blueprint('main', __name__)

# Define routes in the blueprint
@bp.route('/')
def home():
    return jsonify({"message": "Welcome to the Flask app!"})

@bp.route('/status')
def status():
    return jsonify({"status": "OK"})