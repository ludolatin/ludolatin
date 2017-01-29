# -*- coding: utf-8 -*-

from flask import jsonify, request, abort, url_for
from app.api import api
from app.models import User, PhraseList, Answer
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


@api.route('/phraselist/<int:phraselist_id>/answers/')
def get_phraselist_phrases(phraselist_id):
    phraselist = PhraseList.query.get_or_404(phraselist_id)
    if phraselist.creator != current_user.username:
        abort(404)
    return jsonify({
        'answers': [answer.to_dict() for answer in phraselist.answers]
    })


@api.route('/phraselist/<int:todolist_id>/',
           methods=['POST'])
def add_phraselist_answer(phraselist_id):
    phraselist = PhraseList.query.get_or_404(phraselist_id)
    try:
        answer = Answer(
            description=request.json.get('description'),
            phraselist_id=phraselist.id,
            creator=current_user.username
        ).save()
    except:
        abort(400)
    return jsonify(answer.to_dict()), 201
