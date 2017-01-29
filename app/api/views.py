# -*- coding: utf-8 -*-

from flask import jsonify, request, abort, url_for
from app.api import api
from app.models import User, AnswerList, Answer
from app.decorators import admin_required
from flask_login import current_user


@api.route('/')
def get_routes():
    return jsonify({
        'users': url_for('api.get_users', _external=True),
        'answerlists': url_for('api.get_answerlists', _external=True),
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


@api.route('/answerlists/')
def get_answerlists():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    answerlists = user.answerlists
    return jsonify({
        'answerlists': [answerlist.to_dict() for answerlist in answerlists]
    })


@api.route('/answerlist/<int:answerlist_id>/')
def get_answerlist(answerlist_id):
    username = current_user.username
    answerlist = PhraseList.query.get_or_404(answerlist_id)
    if username != answerlist.creator:
        abort(404)
    return jsonify(answerlist.to_dict())


@api.route('/answerlist/', methods=['POST'])
def add_answerlist():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    print user
    print request.json
    try:
        answerlist = PhraseList(
            title=request.json.get('title'),
            creator=user.username
        ).save()
    except:
        abort(400)
    return jsonify(answerlist.to_dict()), 201


@api.route('/answerlist/<int:answerlist_id>/answers/')
def get_answerlist_answers(answerlist_id):
    answerlist = PhraseList.query.get_or_404(answerlist_id)
    if answerlist.creator != current_user.username:
        abort(404)
    return jsonify({
        'answers': [answer.to_dict() for answer in answerlist.answers]
    })


@api.route('/answerlist/<int:todolist_id>/',
           methods=['POST'])
def add_answerlist_answer(answerlist_id):
    answerlist = PhraseList.query.get_or_404(answerlist_id)
    try:
        answer = Answer(
            description=request.json.get('description'),
            answerlist_id=answerlist.id,
            creator=current_user.username
        ).save()
    except:
        abort(400)
    return jsonify(answer.to_dict()), 201
