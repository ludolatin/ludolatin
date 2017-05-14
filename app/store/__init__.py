from flask import Blueprint

store = Blueprint('store', __name__)

from . import views
