from flask import render_template
from flask_login import current_user, login_required

from app.models import Topic, Quiz, Product
from app.topic import topic


@topic.route('/topic/<int:topic_id>')
@login_required
def topic(topic_id):
    current_topic = Topic.query.filter_by(id=topic_id).first_or_404()
    quiz = Quiz.query.filter_by(id=current_user.quiz_id).first()
    topic_size = len(current_topic.quizzes)

    if quiz not in current_topic.quizzes:
        progress = topic_size
    else:
        progress = current_topic.quizzes.index(quiz)

    topic_progress = "%s" % (float(progress) / topic_size * 100)

    recovery = Product.query.filter_by(name="Streak recovery").first()

    return render_template(
        'topic/topic.html',
        title="Topic",
        topic=current_topic,
        topic_progress=topic_progress,
        progress=progress,
        topic_size=topic_size,
        recovery=recovery,
    )
