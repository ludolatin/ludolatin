# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, make_response
from flask_login import current_user, login_required
from sqlalchemy.sql import * # Inefficient

from app.phrases import phrases
from app.phrases.forms import PhraseForm
from app.models import Phrase, PhraseList, EnglishPhrase


def _get_user():
    return current_user.username if current_user.is_authenticated else None


@phrases.route('/phraselist/<int:id>/', methods=['GET', 'POST'])
def phraselist(id):
    phraselist = PhraseList.query.filter_by(id=id).first_or_404()

    form = PhraseForm()
    # POST request:
    if form.validate_on_submit():

        # Retreive the question_id from the cookie
        question_id = request.cookies.get('question_id')

        # Retreive the question from the database
        # (passed to the model where used to determine correctness)
        question = EnglishPhrase.query.filter_by(id=question_id).first_or_404()

        # Retrieve the answer from the POST request data
        answer=form.phrase.data

        # Save to the db via Phrase model
        Phrase(answer, phraselist.id, question, _get_user()).save()

        # Reload the page with a GET request
        return redirect(url_for('phrases.phraselist', id=id))


    # If it wasn't a POST request, must be a GET, so we arrive here

    # Retreive a random English phrase
    englishphrase = EnglishPhrase.query.order_by(func.random()).first()

    # Collection of correct answers previously given, returning just the `phrase` column.
    correct = Phrase.query.with_entities(Phrase.phrase).filter_by(phraselist_id=id, is_correct=True).all()
    # Convert it to a list
    correct = [r for r, in correct]

    # The set of latin translations for the current english phrase (normally only one, but can be many)
    latin_translations = []
    for phrase in englishphrase.latin_translations:
        latin_translations.append(phrase.phrase)

    # True the set (list of unique) latin translations is not in the list of correct answers
    unknown = set(latin_translations).isdisjoint(correct)

    # Rather than returning `render_template`, build a response so that we can attach a cookie
    response = make_response(render_template('phraselist.html', phraselist=phraselist, englishphrase=englishphrase, unknown=unknown, form=form))
    response.set_cookie('question_id', str(englishphrase.id))
    return response
