# -*- coding: utf-8 -*-

from flask import Blueprint

quizzes = Blueprint('quizzes', __name__)

from . import views
