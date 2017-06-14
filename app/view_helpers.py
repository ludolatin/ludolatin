import datetime
import collections

from flask_login import current_user

from app.models import Score


def day_names():
    days = ['Tu', 'W', 'Th', 'F', 'Sa', 'Su', 'M']
    today = datetime.date.today().weekday()
    # Rotate the array so that today is last
    days = days[today:] + days[:today]
    return days


def daily_scores():
    scores_by_day = Score. \
        sum_by_day(). \
        filter_by(user=current_user). \
        order_by(Score.created_at.desc()). \
        limit(7). \
        all()

    # Convert the result to an ordered dictionary of date-keys and scores
    scores_dict = collections.OrderedDict({i[0].date(): int(i[1]) for i in scores_by_day})
    # Create a  of 7 dates from today back
    date_list = [(datetime.date.today() - datetime.timedelta(days=x)) for x in range(0, 7)]

    # Create a list of scores, either matching the date in the list, or 0.
    daily = [scores_dict.get(i, 0) for i in date_list]
    # Reverse so that today is last
    daily.reverse()

    return daily
