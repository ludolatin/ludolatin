from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required

from app.dashboard import dashboard
from app.models import Quiz


def _get_user():
    return current_user if current_user.is_authenticated else None


@dashboard.route('/dashboard')
@login_required
def dashboard():
    user = _get_user()
    quiz = Quiz.query.filter_by(id=user.quiz_id - 1).first()

    topic = quiz.topic
    topic_size = len(topic.quizzes)
    progress = topic.quizzes.index(quiz) + 1

    data = "[%s, %s]" % (progress, topic_size - progress)
    return render_template('dashboard.html', data=data)
