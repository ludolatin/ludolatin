# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required

from app.main import main

def _get_user():
    return current_user.username if current_user.is_authenticated else None


@main.route('/')
@login_required
def index():
    return render_template('index.html')
