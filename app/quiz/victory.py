import datetime

from flask import render_template, redirect, url_for
from flask_login import current_user, login_required

from app.models import Answer, Quiz, Score
from app.quiz import quiz
from app.view_helpers import daily_scores, day_names
from .common import calculate_score


def _get_user():
    return current_user if current_user.is_authenticated else None


@quiz.route('/quiz/<int:quiz_id>/victory', methods=['GET'])
@login_required
def victory(quiz_id):
    user = _get_user()

    last_attempt = Answer.query.filter_by(user=user).order_by(Answer.id.desc()).first().attempt
    last_score = Score.query.filter_by(user=user).order_by(Score.id.desc()).first()

    attempt = last_score.attempt if last_score else 0

    current_quiz = Quiz.query.filter_by(id=user.quiz_id).first()
    current_topic = current_quiz.topic

    if user.streak_start_date is None or user.last_score_age > 36:
        user.streak_start_date = datetime.datetime.utcnow()

    # Make True to allow reloading victory
    # if True:
    if last_attempt > attempt:
        final_score = calculate_score(quiz_id, user)

        user.total_score += final_score
        Score(score=final_score, user=user, quiz_id=quiz_id, attempt=last_attempt)

        # Don't update user.quiz _id if this is a redo
        if user.quiz_id <= quiz_id:
            user.quiz_id += 1
    else:
        return redirect(url_for('quiz.ask', id=user.quiz_id))

    return render_template(
        'quiz/quiz_victory.html',
        title="Quiz",
        id=user.quiz_id,
        score=final_score,
        day_names=day_names(),
        daily_scores=daily_scores(),
        current_topic=current_topic,
    )
