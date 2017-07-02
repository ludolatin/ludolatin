from random import shuffle, randint

from flask import render_template, redirect, request, url_for, make_response
from flask_login import current_user, login_required
from sqlalchemy.sql.expression import func

from app.models import Answer, Sentence, Quiz, User
from app.quiz import quiz
from app.quiz.forms import QuizForm
from .common import template_setup


def _get_user():
    return current_user if current_user.is_authenticated else None


@quiz.route('/quiz/<int:id>/', methods=['GET', 'POST'])
@login_required
def ask(id):
    form = QuizForm()
    user = _get_user()

    # POST request:
    if form.validate_on_submit():

        # Retrieve the question_id from the cookie
        question_id = request.cookies.get('question_id')

        # Retrieve the question from the database
        # (passed to the model where used to determine correctness)
        question = Sentence.query.filter_by(id=question_id).first_or_404()

        # Retrieve the answer from the POST request data
        answer = form.answer.data

        last_answer = Answer.query.filter_by(user=user).order_by(Answer.id.desc()).first()

        attempt = request.cookies.get('attempt') or (last_answer.attempt + 1) if last_answer else 1

        # Save to the db via Answer model
        answer = Answer(answer, question, user, attempt).save()

        # Reload the page with a GET request
        response = make_response(
            redirect(url_for('quiz.validate', id=id))
        )
        response.set_cookie('answer_id', str(answer.id))
        response.set_cookie('attempt', str(attempt))

        return response

    attempt = request.cookies.get('attempt')

    # If it wasn't a POST request, must be a GET, so we arrive here
    current_quiz = Quiz.query.filter_by(id=id).first_or_404()

    # All correctly answered sentences for the current quiz
    answered_sentences = Sentence.query.join(Sentence.answers, Answer.user).\
        filter(Sentence.quiz_id == id, Answer.is_correct or Answer.is_correct is None, User.id == user.id, Answer.attempt == attempt).all()

    # All sentences for the current quiz
    all_sentences = Sentence.query.filter(Sentence.quiz_id == id).order_by(func.random()).all()

    # The set of unanswered questions
    # TODO: can we do this in a single DB query instead of the two above?
    questions = set(all_sentences) - set(answered_sentences)

    # If there are no unanswered questions, bump level
    if len(questions) == 0:
        response = make_response(
            redirect(url_for('quiz.victory', quiz_id=id))
        )
        response.set_cookie('attempt', '', expires=0)
        return response

    question = list(questions)[0]
    progress, unknown = template_setup(question, id)

    templates = {
        'simple': 'quiz/simple.html',
        'word-pick': 'quiz/word_pick.html',
    }

    words = []

    if question.type == "word-pick":
        quiz_question = Sentence.query.filter(Sentence.quiz == current_quiz, Sentence.id != question.id)\
            .order_by(func.random()).first()
        words = question.translations[randint(0, len(question.translations) - 1)].text.split(" ")
        words += quiz_question.translations[0].text.split(" ")
        words = list(filter(None, words))
        words = list(set(words))
        shuffle(words)

    # Rather than returning `render_template`, build a response so that we can attach a cookie to it
    response = make_response(
        render_template(
            templates[question.type],
            title="LudoLatin",
            question=question,
            unknown=unknown,
            form=form,
            progress=progress,
            last_progress=progress,
            quiz=current_quiz,
            words=words,
        )
    )

    response.set_cookie('question_id', str(question.id))
    return response
