from flask import render_template, request
from flask_login import current_user, login_required

from app.models import Answer, Sentence, Quiz
from app.quiz import quiz
from app.quiz.forms import QuizForm
from .common import template_setup, correct_answers


def _get_user():
    return current_user if current_user.is_authenticated else None


@quiz.route('/quiz/<int:id>/validate', methods=['GET'])
@login_required
def validate(id):
    form = QuizForm()

    # Retrieve the question_id from the cookie
    question_id = request.cookies.get('question_id')

    # Retrieve the answer from the cookie
    answer_id = request.cookies.get('answer_id')

    # Retrieve the question from the database
    # (passed to the model where used to determine correctness)
    question = Sentence.query.filter_by(id=question_id).first_or_404()

    # Retrieve the question from the database
    # (passed to the model where used to determine correctness)
    answer = Answer.query.filter_by(id=answer_id).first()

    progress, unknown = template_setup(question, id)

    quiz = Quiz.query.filter_by(id=id).first_or_404()

    # Get previous progress for progress bar animation
    if answer.is_correct or answer.is_correct is None:
        last_progress = float(len(correct_answers(id)) - 1) / Sentence.query.filter_by(quiz_id=id).count() * 100
    else:
        last_progress = progress

    # Rather than returning `render_template`, build a response so that we can attach a cookie to it
    return render_template(
        'quiz/quiz_validate.html',
        title="LudoLatin",
        answer=answer,
        question=question,
        unknown=unknown,
        form=form,
        progress=progress,
        last_progress=last_progress,
        quiz=quiz,
    )
