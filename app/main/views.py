from flask import render_template, redirect, url_for
from flask_login import current_user
from app.main import main


@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    else:
        return render_template('index.html')
