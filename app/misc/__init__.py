from flask import Blueprint

misc = Blueprint('misc', __name__)

from . import views
