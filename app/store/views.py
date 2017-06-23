from flask import render_template, request
from flask_login import current_user, login_required

from app.models import Product
from app.store import store
from app.view_helpers import daily_scores, day_names


def _get_user():
    return current_user if current_user.is_authenticated else None


@store.route('/store')
@login_required
def store():
    if current_user.last_score_age and current_user.streak:
        streak_time_left = 36 - current_user.last_score_age
    else:
        streak_time_left = 36

    return render_template(
        'store.html',
        title="Store",
        products=Product.query.all(),
        day_names=day_names(),
        daily_scores=daily_scores(),
        referrer=request.referrer,
        streak_time_left=streak_time_left,
    )
