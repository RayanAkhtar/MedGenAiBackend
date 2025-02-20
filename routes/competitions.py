
from flask import jsonify, send_from_directory, Blueprint, request
from services.competitions import get_all_competitions, get_competition, submit_competition_score
bp = Blueprint('competitions', __name__)

@bp.route('/api/competitions/all', methods=['GET'])
def get_competition():
    """
    Returns a list of all competitions
    """
    print("Fetching competitions")
    return get_all_competitions()
  
@bp.route('/api/competitions/specific', methods=['GET, POST'])
def get_specific():
  json_data = request.get_json()
  print(f"Getting competiton with ID: {json_data.competition_id}")
  return get_competition(json_data.competition_id);

@bp.route('/api/competitions/submit', methods=['POST'])
def submit():
  json_data = request.get_json()
  print(f"Submitting to competiton with ID: {json_data.competition_id}, for user: {json_data.user_id}")
  return submit_competition_score(json_data.competition_id);
