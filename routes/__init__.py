from flask import Blueprint

bp = Blueprint('main', __name__)

from . import main, profile, game, auth, user_dashboard