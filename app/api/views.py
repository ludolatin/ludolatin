# -*- coding: utf-8 -*-

from flask import jsonify, request, abort, url_for
from sqlalchemy.sql import func
from app.api import api
from app.models import User, PhraseList, Phrase, EnglishPhrase, LatinPhrase
from app.decorators import admin_required
from flask_login import current_user

@api.route('/')
def get_routes():
    return jsonify({
        'users': url_for('api.get_users', _external=True),
        'phraselists': url_for('api.get_phraselists', _external=True),
    })


@api.route('/users/')
def get_users():
    return jsonify({'users': [user.to_dict() for user in User.query.all()]})


@api.route('/user/<string:username>/')
def get_user(username):
    print current_user
    user = User.query.filter_by(username=username).first_or_404()
    return jsonify(user.to_dict())


@api.route('/user/', methods=['POST'])
def add_user():
    try:
        user = User(
            username=request.json.get('username'),
            email=request.json.get('email'),
            password=request.json.get('password'),
        ).save()
    except:
        abort(400)
    return jsonify(user.to_dict()), 201


@api.route('/user/<string:username>/', methods=['DELETE'])
@admin_required
def delete_user(username):
    user = User.query.get_or_404(username=username)
    try:
        if username == request.json.get('username'):
            user.delete()
            return jsonify()
        else:
            abort(400)
    except:
        abort(400)

@api.route('/phraselists/')
def get_phraselists():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    phraselists = user.phraselists
    return jsonify({
        'phraselists': [phraselist.to_dict() for phraselist in phraselists]
    })


@api.route('/phraselist/<int:phraselist_id>/')
def get_phraselist(phraselist_id):
    username = current_user.username
    phraselist = PhraseList.query.get_or_404(phraselist_id)
    if username != phraselist.creator:
        abort(404)
    return jsonify(phraselist.to_dict())

@api.route('/phraselist/', methods=['POST'])
def add_phraselist():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    print user
    print request.json
    try:
        phraselist = PhraseList(
            title=request.json.get('title'),
            creator=user.username
        ).save()
    except:
        abort(400)
    return jsonify(phraselist.to_dict()), 201


@api.route('/phraselist/<int:phraselist_id>/phrases/')
def get_phraselist_phrases(phraselist_id):
    phraselist = PhraseList.query.get_or_404(phraselist_id)
    if phraselist.creator != current_user.username:
        abort(404)
    return jsonify({
        'phrases': [phrase.to_dict() for phrase in phraselist.phrases]
    })

@api.route('/phraselist/<int:phraselist_id>/', methods=['POST'])
def add_phraselist_phrase(phraselist_id):
    phraselist = PhraseList.query.get_or_404(phraselist_id)
    try:
        phrase = Phrase(
            description=request.json.get('description'),
            phraselist_id=phraselist.id,
            creator=current_user.username
        ).save()
    except:
        abort(400)
    return jsonify(phrase.to_dict()), 201


@api.route('/englishphrases/')
def get_englishphrases():
    phrases = EnglishPhrase.query.all()
    return jsonify({'englishphrases': [phrase.to_dict() for phrase in phrases]})


@api.route('/latinphrases/')
def get_latinphrases():
    phrases = LatinPhrase.query.all()
    return jsonify({'latinphrases': [phrase.to_dict() for phrase in phrases]})


@api.route('/englishphrase/<int:id>/')
def get_englishphrase(id):
    englishphrase = EnglishPhrase.query.filter_by(id=id).first_or_404()
    return jsonify({
        'created_at': englishphrase.created_at,
        'phrase': englishphrase.phrase,
        'latin_translations': [phrase.to_dict() for phrase in englishphrase.latin_translations]
        })


@api.route('/latinphrase/<int:id>/')
def get_latinphrase(id):
    latinphrase = LatinPhrase.query.filter_by(id=id).first_or_404()
    return jsonify({
        'created_at': latinphrase.created_at,
        'phrase': latinphrase.phrase,
        'english_translations': [phrase.to_dict() for phrase in latinphrase.english_translations]
        })


@api.route('/randomenglishphrase/')
def get_randomenglishphrase():
    englishphrase = EnglishPhrase.query.order_by(func.random()).first()
    return jsonify({
        'created_at': englishphrase.created_at,
        'phrase': englishphrase.phrase,
        'latin_translations': [phrase.to_dict() for phrase in englishphrase.latin_translations]
        })


@api.route('/randomlatinphrase/')
def get_lrandomatinphrase():
    latinphrase = LatinPhrase.query.order_by(func.random()).first()
    return jsonify({
        'created_at': latinphrase.created_at,
        'phrase': latinphrase.phrase,
        'english_translations': [phrase.to_dict() for phrase in latinphrase.english_translations]
        })
