import datetime

from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required

from app.topic import topic
from app.models import Topic, Quiz


def _get_user():
    return current_user if current_user.is_authenticated else None


@topic.route('/topic/<int:id>')
@login_required
def topic(id):
    user = _get_user()

    topic = Topic.query.filter_by(id=id).first_or_404()

    quiz = Quiz.query.filter_by(id=user.quiz_id).first()

    topic_size = len(topic.quizzes)

    if quiz not in topic.quizzes:
        progress = topic_size
    else:
        progress = topic.quizzes.index(quiz)

    topic_progress = "%s" % (float(progress) / topic_size  * 100)

    return render_template(
        'topic.html',
        topic=topic,
        topic_progress=topic_progress,
        progress=progress,
        topic_size=topic_size,
    )
