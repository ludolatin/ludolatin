from flask import render_template, request
from flask_login import current_user, login_required

from app.models import Product
from app.store import store
from app.view_helpers import daily_scores, day_names, leaderboard


def _get_user():
    return current_user if current_user.is_authenticated else None


@store.route('/store')
@login_required
def store():
    if current_user.last_score_age and current_user.streak:
        streak_time_left = 36 - current_user.last_score_age
    else:
        streak_time_left = 36

    pictures = [
        {"id": 1, "name": "Sky (default)", "filename": "profile-1.png"},
        {"id": 2, "name": "Relish", "filename": "profile-2.png"},
        {"id": 3, "name": "Mango", "filename": "profile-3.png"},
        {"id": 4, "name": "Cherry", "filename": "profile-4.png"},
        {"id": 5, "name": "Grape", "filename": "profile-5.png"},
        {"id": 6, "name": "Slate", "filename": "profile-6.png"},
    ]

    return render_template(
        'store.html',
        title="Store",
        products=Product.query.all(),
        day_names=day_names(),
        daily_scores=daily_scores(),
        referrer=request.referrer,
        streak_time_left=streak_time_left,
        pictures=pictures,
        leaderboard=leaderboard()
    )
