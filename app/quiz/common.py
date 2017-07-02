from flask import request
from flask_login import current_user

from app.models import Answer, Sentence


def _get_user():
    return current_user if current_user.is_authenticated else None


def correct_answers(id):
    attempt = request.cookies.get('attempt')

    # Collection of correct answers previously given, returning just the `text` column
    correct = Answer.query.join(Sentence).with_entities(Answer.text).filter(
        Answer.is_correct or Answer.is_correct is None,
        Sentence.quiz_id == id,
        Answer.user == _get_user(),
        Answer.attempt == attempt,
    ).all()
    # Convert it to a list, and the list to a set
    correct = set([r for r, in correct])
    return correct


def template_setup(question, id):
    correct = correct_answers(id)

    # The percentage of questions that have been answered correctly
    progress = float(len(correct)) / Sentence.query.filter_by(quiz_id=id).count() * 100

    # True if the set (list of unique) latin translations is not in the set of correct answers
    # Used in quiz_base for hint
    unknown = not(Answer.query.join(Sentence).filter(
        Sentence.quiz_id == id,
        Answer.sentence == question,
        Answer.user == _get_user(),
        Answer.is_correct
    ).count())

    return progress, unknown

def calculate_score(quiz_id, user):
    score = Sentence.query.filter_by(quiz_id=quiz_id).count() * 2
    neg_score = Answer.query.join(Sentence) \
        .filter(Answer.is_correct is False, Answer.user == user, Sentence.quiz_id == quiz_id).count()
    final_score = score - neg_score
    if final_score < 3:
        final_score = 3
    return final_score
