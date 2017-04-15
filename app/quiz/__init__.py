from flask import Blueprint

quiz = Blueprint('quiz', __name__)

from . import views
