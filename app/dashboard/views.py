import datetime

from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required

from app.dashboard import dashboard
from app.models import Quiz, Sentence, Answer, Score, Topic


def _get_user():
    return current_user if current_user.is_authenticated else None


@dashboard.route('/dashboard')
@login_required
def dashboard():
    user = _get_user()

    quiz = Quiz.query.filter_by(id=user.quiz_id).first()

    current_topic = quiz.topic
    topic_size = len(current_topic.quizzes)

    progress = current_topic.quizzes.index(quiz)
    topic_progress = "%s" % (float(progress) / topic_size  * 100)
    topics = Topic.query.filter_by().all()

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
        topic_progress=topic_progress,
        days=days,
        daily=daily,
        topics=topics,
        current_topic=current_topic,
        topic_size=topic_size,
        progress=progress,
    )
