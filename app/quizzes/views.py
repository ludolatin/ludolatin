# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, make_response
from flask_login import current_user, login_required
from sqlalchemy.sql import * # Inefficient

from app.quizzes import quizzes
from app.quizzes.forms import QuizForm
from app.models import Answer, Sentence, Language, Quiz


def _get_user():
    return current_user if current_user.is_authenticated else None


@quizzes.route('/quiz/<int:id>/', methods=['GET', 'POST'])
@login_required
def ask(id):
    form = QuizForm()

    # POST request:
    if form.validate_on_submit():

        # Retrieve the question_id from the cookie
        question_id = request.cookies.get('question_id')

        # Retrieve the question from the database
        # (passed to the model where used to determine correctness)
        question = Sentence.query.filter_by(id=question_id).first_or_404()

        # Retrieve the answer from the POST request data
        answer = form.answer.data

        # Save to the db via Answer model
        # Answer(answer, answerlist.id, question, _get_user()).save()
        answer = Answer(answer, question, _get_user()).save()

        # Reload the page with a GET request
        response = make_response(
            redirect(url_for('quizzes.validate', id=id))
        )
        response.set_cookie('answer_id', str(answer.id))
        return response

    # If it wasn't a POST request, must be a GET, so we arrive here

    # Retrieve a random English phrase
    question = Sentence.query.join(Sentence.language, Sentence.quiz).\
        filter(Language.name == "English", Quiz.id == id).order_by(func.random()).first()

    progress, unknown, quiz = template_setup(question, id)

    # Rather than returning `render_template`, build a response so that we can attach a cookie to it
    response = make_response(
        render_template(
            'quiz.html',
            question=question,
            unknown=unknown,
            form=form,
            progress=progress,
            quiz=quiz
        )
    )

    response.set_cookie('question_id', str(question.id))
    return response


@quizzes.route('/quiz/<int:id>/validate', methods=['GET'])
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

    progress, unknown, quiz = template_setup(question, id)

    # Rather than returning `render_template`, build a response so that we can attach a cookie to it
    return render_template(
        'quiz_validate.html',
        answer=answer,
        question=question,
        unknown=unknown,
        form=form,
        progress=progress,
        quiz=quiz
    )


def template_setup(question, id):
    # Collection of correct answers previously given, returning just the `text` column
    correct = Answer.query.with_entities(Answer.text).filter_by(is_correct=True, user=_get_user()).all()

    # Convert it to a list, and the list to a set
    correct = set([r for r, in correct])

    # The list of latin translations for the current english phrase (normally only one, but can be many)
    translations = []
    for translation in question.translations:
        translations.append(translation.text)

    # True if the set (list of unique) latin translations is not in the set of correct answers
    unknown = set(translations).isdisjoint(correct)

    # The percentage of questions that have been answered correctly
    progress = float(len(correct)) / Sentence.query.count() * 100

    quiz = Quiz.query.filter_by(id=id).first()

    return progress, unknown, quiz

