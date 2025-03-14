
from flask import jsonify, send_from_directory, Blueprint, request
from services.competitions import get_all_competitions, get_competition, get_game_by_game_id, submit_competition_score, create_competition
bp = Blueprint('competitions', __name__)


@bp.route('/api/competitions/create', methods=['POST'])
def create():
  json_data = request.get_json()
  print(json_data)
  print(f"Creating competition : {json_data.get('name')}")
  return create_competition(json_data.get('name'), json_data.get('expiry'), json_data.get('game_code'))

@bp.route('/api/competitions/all', methods=['GET'])
def get_competition_all():
    """
    Returns a list of all competitions
    """
    print("Fetching competitions")
    return get_all_competitions()
  
@bp.route('/api/competitions/specific', methods=['POST'])
def get_specific():
  json_data = request.get_json()
  print(f"Getting competiton with ID: {json_data.get('competition_id')}")
  return get_competition(json_data.get('competition_id'));

@bp.route('/api/competitions/submit', methods=['POST'])
def submit():
  json_data = request.get_json()
  print(f"Submitting to competiton with ID: {json_data.competition_id}, for user: {json_data.user_id}")
  return submit_competition_score(json_data.competition_id, json_data.user_id, json_data.score)


@bp.route('/api/getGame/<int:game_id>', methods=['GET'])
def get_game(game_id):
    return jsonify(get_game_by_game_id(game_id))