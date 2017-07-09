from flask import render_template, request
from flask_login import current_user, login_required, session

from app.models import Answer, Sentence, Quiz
from app.quiz import quiz
from app.quiz.forms import QuizForm
from .common import template_setup, correct_answers


def _get_user():
    return current_user if current_user.is_authenticated else None


@quiz.route('/quiz/<int:quiz_id>/validate', methods=['GET'])
@login_required
def validate(quiz_id):
    form = QuizForm()

    question_id = request.cookies.get('question_id')
    answer_id = request.cookies.get('answer_id')
    question = Sentence.query.filter_by(id=question_id).first_or_404()
    answer = Answer.query.filter_by(id=answer_id).first()
    progress, unknown = template_setup(question, quiz_id)
    current_quiz = Quiz.query.filter_by(id=quiz_id).first_or_404()
    words = session.get('words', None)
    picture = session.get('answer', None)

    # Get previous progress for progress bar animation
    if answer.is_correct or answer.is_correct is None:
        last_progress = float(len(correct_answers(quiz_id)) - 1) / Sentence.query.filter_by(quiz_id=quiz_id).count() * 100
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
        quiz=current_quiz,
        words=words,
        picture=picture,
    )
