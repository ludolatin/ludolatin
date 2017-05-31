import datetime

from flask import render_template, request
from flask_login import current_user, login_required

from app.models import Product, Score
from app.store import store


def _get_user():
    return current_user if current_user.is_authenticated else None


@store.route('/store')
@login_required
def store():
    user = _get_user()

    products = Product.query.all()

    if user:
        # TODO: DRY this x 3 (dashboard/views, store/views, quiz/views)
        daily = Score.\
            sum_by_day().\
            filter_by(user=user).\
            order_by(Score.created_at.desc()).\
            limit(7).\
            all()

        # remove the tuple wrappers
        daily = [int(i[0]) for i in daily]
        # Pad to seven entries
        daily += [0] * (7 - len(daily))
        # most recent last
        daily.reverse()

        days = ['Tu',  'W', 'Th', 'F', 'Sa', 'Su', 'M']
        today = datetime.date.today().weekday()
        # Rotate the array so that today is last
        days = days[today:] + days[:today]

        referrer = request.referrer

        return render_template(
            'store.html',
            title="LudoLatin - Store",
            products=products,
            days=days,
            daily=daily,
            referrer=referrer,
        )
