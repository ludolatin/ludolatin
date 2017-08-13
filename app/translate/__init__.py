from flask import Blueprint

translate = Blueprint('translate', __name__)

from . import views
