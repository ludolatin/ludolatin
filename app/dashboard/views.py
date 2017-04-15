import datetime

from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required

from app.dashboard import dashboard
from app.models import Quiz, Sentence, Answer, Score


def _get_user():
    return current_user if current_user.is_authenticated else None


@dashboard.route('/dashboard')
@login_required
def dashboard():
    user = _get_user()

    if user.quiz_id == 1:
        quiz_id = 1
    else:
        quiz_id = user.quiz_id - 1
    quiz = Quiz.query.filter_by(id=quiz_id).first()

    topic = quiz.topic
    topic_size = len(topic.quiz)

    if user.quiz_id == 1:
        progress = 0
    else:
        progress = topic.quiz.index(quiz) + 1

    data = "[%s, %s]" % (progress, topic_size - progress)

    daily = Score.\
        sum_by_day().\
        filter_by(user=_get_user()).\
        order_by(Score.created_at.desc()).\
        limit(7).\
        all()

    # remove the tuple wrappers
    daily = [i[0] for i in daily]
    # Pad to seven entries
    daily += [0] * (7 - len(daily))
    # most recent last
    daily.reverse()

    days = ['Tu',  'W', 'Th', 'F', 'Sa', 'Su', 'M']
    today = datetime.date.today().weekday()
    # Rotate the array so that today is last
    days = days[today:] + days[:today]

    return render_template(
        'dashboard.html',
        data=data,
        days=days,
        daily=daily
    )
