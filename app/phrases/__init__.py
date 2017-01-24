# -*- coding: utf-8 -*-

from flask import Blueprint

phrases = Blueprint('phrases', __name__)

from . import views
