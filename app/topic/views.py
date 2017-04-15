import datetime

from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required

from app.topic import topic
from app.models import Quiz, Sentence, Answer, Score


def _get_user():
    return current_user if current_user.is_authenticated else None


@topic.route('/topic')
@login_required
def topic():
    user = _get_user()

    if user.quiz_id == 1:
        quiz_id = 1
    else:
        quiz_id = user.quiz_id - 1
    quiz = Quiz.query.filter_by(id=quiz_id).first()

    current_topic = quiz.topic

    return render_template(
        'topic.html',
        topic=current_topic
    )
