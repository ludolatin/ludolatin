from flask import render_template
from flask_login import current_user, login_required

from app.models import Topic, Quiz, Product
from app.topic import topic


def _get_user():
    return current_user if current_user.is_authenticated else None


@topic.route('/topic/<int:id>')
@login_required
def topic(id):
    user = _get_user()

    current_topic = Topic.query.filter_by(id=id).first_or_404()

    quiz = Quiz.query.filter_by(id=user.quiz_id).first()

    topic_size = len(current_topic.quizzes)

    if quiz not in current_topic.quizzes:
        progress = topic_size
    else:
        progress = current_topic.quizzes.index(quiz)

    topic_progress = "%s" % (float(progress) / topic_size * 100)

    recovery = Product.query.filter_by(name="Streak recovery").first()

    return render_template(
        'topic.html',
        title="LudoLatin - Topic",
        topic=current_topic,
        topic_progress=topic_progress,
        progress=progress,
        topic_size=topic_size,
        recovery=recovery,
    )
