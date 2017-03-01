from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required

from app.dashboard import dashboard


def _get_user():
    return current_user.username if current_user.is_authenticated else None


@dashboard.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
