# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, make_response
from flask_login import current_user, login_required
from sqlalchemy.sql import * # Inefficient

from app.quiz import quiz
from app.quiz.forms import QuizForm
from app.models import Answer, EnglishPhrase


def _get_user():
    return current_user.username if current_user.is_authenticated else None


@quiz.route('/quiz/<int:id>/', methods=['GET', 'POST'])
@login_required
def ask(id):
    # answerlist = AnswerList.query.filter_by(id=id).first_or_404()
    form = QuizForm()

    # POST request:
    if form.validate_on_submit():

        # Retrieve the question_id from the cookie
        question_id = request.cookies.get('question_id')

        # Retrieve the question from the database
        # (passed to the model where used to determine correctness)
        question = EnglishPhrase.query.filter_by(id=question_id).first_or_404()

        # Retrieve the answer from the POST request data
        answer = form.answer.data

        # Save to the db via Answer model
        # Answer(answer, answerlist.id, question, _get_user()).save()
        answer = Answer(answer, question, _get_user()).save()
        print answer

        # Reload the page with a GET request
        response = make_response(
            redirect(url_for('quiz.validate', id=id))
        )
        response.set_cookie('answer_id', str(answer.id))
        return response

    # If it wasn't a POST request, must be a GET, so we arrive here

    # Retrieve a random English phrase
    question = EnglishPhrase.query.order_by(func.random()).first()

    # Collection of correct answers previously given, returning just the `text` column
    correct = Answer.query.with_entities(Answer.text).filter_by(is_correct=True, creator=_get_user()).all()
    # correct = Answer.query.with_entities(Answer.text).filter_by(answerlist_id=id, is_correct=True).all()

    # Convert it to a list, and the list to a set
    correct = set([r for r, in correct])

    # The list of latin translations for the current english phrase (normally only one, but can be many)
    translations = []
    for translation in question.translations:
        translations.append(translation.text)

    # True if the set (list of unique) latin translations is not in the set of correct answers
    unknown = set(translations).isdisjoint(correct)

    # The percentage of questions that have been answered correctly
    progress = float(len(correct)) / EnglishPhrase.query.count() * 100

    # Rather than returning `render_template`, build a response so that we can attach a cookie to it
    response = make_response(
        render_template(
            'quiz.html',
            question=question,
            unknown=unknown,
            form=form,
            progress=progress
        )
    )

    # response = make_response(
    #     render_template(
    #         'quiz.html',
    #         answerlist=answerlist,
    #         question=question,
    #         unknown=unknown,
    #         form=form,
    #         progress=progress
    #    )
    # )
    response.set_cookie('question_id', str(question.id))
    return response


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
    question = EnglishPhrase.query.filter_by(id=question_id).first_or_404()

    # # Retrieve a random English phrase
    # question = EnglishPhrase.query.order_by(func.random()).first()

    # Retrieve the question from the database
    # (passed to the model where used to determine correctness)
    answer = Answer.query.filter_by(id=answer_id).first()

    # Collection of correct answers previously given, returning just the `text` column
    correct = Answer.query.with_entities(Answer.text).filter_by(is_correct=True, creator=_get_user()).all()
    # correct = Answer.query.with_entities(Answer.text).filter_by(answerlist_id=id, is_correct=True).all()

    # Convert it to a list, and the list to a set
    correct = set([r for r, in correct])

    # The list of latin translations for the current english phrase (normally only one, but can be many)
    translations = []
    for translation in question.translations:
        translations.append(translation.text)

    # True if the set (list of unique) latin translations is not in the set of correct answers
    unknown = set(translations).isdisjoint(correct)

    # The percentage of questions that have been answered correctly
    progress = float(len(correct)) / EnglishPhrase.query.count() * 100

    # Rather than returning `render_template`, build a response so that we can attach a cookie to it
    return render_template(
        'quiz_validate.html',
        answer=answer,
        question=question,
        unknown=unknown,
        form=form,
        progress=progress
    )
