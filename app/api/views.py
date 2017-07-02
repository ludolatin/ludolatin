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
@admin_required
def get_users():
    return jsonify({
        'users': [user.to_dict() for user in User.query.all()],
        'user_count': url_for('api.user_count', _external=True),
    })


@api.route('/users/count')
def user_count():
    return jsonify({'user_count': User.query.count()})


@api.route('/user/<int:id>/')
@admin_required
def get_user(id):
    print current_user
    user = User.query.get_or_404(id)
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


@api.route('/user/<int:id>/', methods=['DELETE'])
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
        'triple_or_nothing': url_for('api.triple_or_nothing', _external=True),
    })


# TODO: Make POST
@api.route('/store/recover_streak/', methods=['GET'])
def recover_streak():
    try:
        product = Product.query.filter_by(name="Streak recovery").first()
        if product.available:
            current_user.total_score -= product.total_price

            Purchase(
                product=product,
                price=product.total_price,
                user_id=current_user.id,
            ).save()

            Score(
                user_id=current_user.id,
                created_at=datetime.datetime.utcnow(),
                score=0
            ).save()
    except:
        abort(400)
    return jsonify(current_user.to_dict()), 200


# TODO: Make POST
@api.route('/store/triple_or_nothing/', methods=['GET'])
def triple_or_nothing():
    product = Product.query.filter_by(name="Triple or nothing").first()
    result = ""
    if product.available:
        try:
            Purchase(
                product=product,
                price=product.total_price,
                user_id=current_user.id,
            ).save()

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
    }), 200


@api.route('/store/profile_pictures/<int:picture_id>', methods=['GET'])
def profile_pictures(picture_id):
    product = Product.query.filter_by(name="Profile picture").first()
    if product.available:
        try:
            Purchase(
                product=product,
                price=product.total_price,
                user_id=current_user.id,
            ).save()
            current_user.profile_picture = picture_id
            current_user.total_score -= product.total_price
        except:
            abort(400)
    return jsonify(current_user.to_dict()), 200
