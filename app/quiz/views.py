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
def quiz(id):
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
        answer=form.answer.data

        # Save to the db via Answer model
        # Answer(answer, answerlist.id, question, _get_user()).save()
        Answer(answer, question, _get_user()).save()

        # Reload the page with a GET request
        return redirect(url_for('quiz.quiz', id=id))

    # If it wasn't a POST request, must be a GET, so we arrive here

    # Retrieve a random English phrase
    englishphrase = EnglishPhrase.query.order_by(func.random()).first()

    # Collection of correct answers previously given, returning just the `text` column
    correct = Answer.query.with_entities(Answer.text).filter_by(is_correct=True).all()
    # correct = Answer.query.with_entities(Answer.text).filter_by(answerlist_id=id, is_correct=True).all()

    # Convert it to a list, and the list to a set
    correct = set([r for r, in correct])

    # The list of latin translations for the current english phrase (normally only one, but can be many)
    translations = []
    for phrase in englishphrase.translations:
        translations.append(phrase.phrase)

    # True if the set (list of unique) latin translations is not in the set of correct answers
    unknown = set(translations).isdisjoint(correct)

    # The percentage of questions that have been answered correctly
    progress = float(len(correct)) / EnglishPhrase.query.count() * 100

    # Rather than returning `render_template`, build a response so that we can attach a cookie to it
    response = make_response(
        render_template(
            'quiz.html',
            englishphrase=englishphrase,
            unknown=unknown,
            form=form,
            progress=progress
        )
    )

    # response = make_response(
    #     render_template(
    #         'quiz.html',
    #         answerlist=answerlist,
    #         englishphrase=englishphrase,
    #         unknown=unknown,
    #         form=form,
    #         progress=progress
    #    )
    # )
    response.set_cookie('question_id', str(englishphrase.id))
    return response
