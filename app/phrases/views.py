# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required

from app.phrases import phrases
from app.phrases.forms import PhraseForm
from app.models import Phrase, PhraseList


def _get_user():
    return current_user.username if current_user.is_authenticated else None


@phrases.route('/phraselist/<int:id>/', methods=['GET', 'POST'])
def phraselist(id):
    phraselist = PhraseList.query.filter_by(id=id).first_or_404()
    form = PhraseForm()
    if form.validate_on_submit():
        Phrase(form.phrase.data, phraselist.id, _get_user()).save()
        return redirect(url_for('phrases.phraselist', id=id))
    return render_template('phraselist.html', phraselist=phraselist, form=form)
