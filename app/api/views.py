# -*- coding: utf-8 -*-

from flask import jsonify, request, abort, url_for
from app.api import api
from app.models import User, Answer
from app.decorators import admin_required
from flask_login import current_user


@api.route('/')
def get_routes():
    return jsonify({
        'users': url_for('api.get_users', _external=True),
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
