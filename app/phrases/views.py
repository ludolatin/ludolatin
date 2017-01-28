# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, make_response
from flask_login import current_user, login_required
from sqlalchemy.sql import func

from app.phrases import phrases
from app.phrases.forms import PhraseForm
from app.models import Phrase, PhraseList, EnglishPhrase


def _get_user():
    return current_user.username if current_user.is_authenticated else None


@phrases.route('/phraselist/<int:id>/', methods=['GET', 'POST'])
def phraselist(id):
    phraselist = PhraseList.query.filter_by(id=id).first_or_404()

    form = PhraseForm()
    if form.validate_on_submit():
        question_id = request.cookies.get('question_id')
        question = EnglishPhrase.query.filter_by(id=question_id).first_or_404()
        answer=form.phrase.data

        Phrase(answer, phraselist.id, question, _get_user()).save()
        return redirect(url_for('phrases.phraselist', id=id))

    englishphrase = EnglishPhrase.query.order_by(func.random()).first()
    print "\nenglishphrase: "
    print englishphrase
    print

    response = make_response(render_template('phraselist.html', phraselist=phraselist, englishphrase=englishphrase, form=form))
    response.set_cookie('question_id', str(englishphrase.id))
    return response

