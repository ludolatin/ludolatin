from flask import Blueprint

topic = Blueprint('topic', __name__)

from . import views
