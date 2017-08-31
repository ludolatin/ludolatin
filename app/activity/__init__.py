from flask import Blueprint

activity = Blueprint('activity', __name__)

from . import views
