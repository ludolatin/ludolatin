import datetime
from random import randint
from flask import jsonify, request, abort, url_for
from flask_login import current_user

from app.api import api
from app.decorators import admin_required
from app.models import User, Score, Product, Purchase


@api.route('/')
def get_routes():
    return jsonify({
        'users': url_for('api.get_users', _external=True),
        'store': url_for('api.get_store_routes', _external=True),
    })


@api.route('/users/')
def get_users():
    return jsonify({'users': [user.to_dict() for user in User.query.all()]})


@api.route('/users/count')
def user_number():
    return jsonify({'user number': User.query.count()})


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


@api.route('/store/')
def get_store_routes():
    return jsonify({
        'recover_streak': url_for('api.recover_streak', _external=True),
    })


# TODO: Make POST
@api.route('/store/recover_streak/', methods=['GET'])
def recover_streak():
    try:
        product = Product.query.filter_by(name="Streak recovery").first()
        if product.available:
            current_user.total_score -= product.total_price

            Score(
                user_id=current_user.id,
                created_at=datetime.datetime.utcnow(),
                score=0
            ).save()

            Purchase(
                product=product,
                price=product.total_price,
                user_id=current_user.id,
            ).save()
    except:
        abort(400)
    return jsonify(current_user.to_dict()), 201


# TODO: Make POST
@api.route('/store/triple_or_nothing/', methods=['GET'])
def triple_or_nothing():
    result = ""
    try:
        if randint(0, 2) == 0:
            current_user.total_score += (int(current_user.total_score / 4)) * 2
            result = "success"
        else:
            current_user.total_score -= int(current_user.total_score / 4)
            result = "failure"
    except:
        abort(400)
    return jsonify({
        'user': current_user.to_dict(),
        'result': result,
    }), 201
