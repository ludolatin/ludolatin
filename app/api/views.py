import datetime
from random import randint
from flask import jsonify, abort, url_for, request
from flask_login import current_user

from app.api import api
from app.models import User, Score, Product, Purchase, Comment
from app.view_helpers import recaptcha_verify


@api.route('/')
def welcome():
    return "Welcome to the LudoLatin API. Read the docs at github.com/ludolatin/ludolatin/blob/master/API.md"


@api.route('/users/me/')
def get_user():
    return jsonify(current_user.to_dict())


@api.route('/posts/<int:post_id>/')
def get_post(post_id):
    return "post", post_id


@api.route('/users/<username>/comments/')
def get_user_comments(username):
    user = User.query.filter_by(username=username).first()
    comments = [{
        "body": comment.body,
        "id": comment.id,
        "body_html": comment.body_html,
        "created_at": comment.created_at,
        "user_id": comment.user_id,
        "post_id": comment.post_id
    } for comment in user.comments if not comment.disabled]
    return jsonify(comments)


@api.route('/posts/<int:post_id>/comments/')
def get_post_comments(post_id):
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
        comments = [{
            "body": comment.body,
            "id": comment.id,
            "body_html": comment.body_html,
            "created_at": comment.created_at,
            "user": {"username": comment.user.username, "profile_picture": comment.user.profile_picture},
            "post_id": comment.post_id
        } for comment in comments if not comment.disabled]
        return jsonify(comments)


@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    comment = {
        "body": comment.body,
        "id": comment.id,
        "body_html": comment.body_html,
        "created_at": comment.created_at,
        "user": {"username": comment.user.username, "profile_picture": comment.user.profile_picture},
        "post_id": comment.post_id
    }
    return jsonify(comment)


@api.route('/posts/<int:post_id>/comments/', methods=['POST'])
def new_post_comment(post_id):
    g_recaptcha_response = request.get_json(force=True)[1]['value']
    if recaptcha_verify(g_recaptcha_response):
        try:
            comment_body = request.get_json(force=True)[0]['value']
            comment = Comment(
                body=comment_body,
                user=current_user,
                post_id=post_id,
            ).save()
            return jsonify(comment.to_json()), 201
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
        return jsonify(current_user.to_dict()), 200
    except:
        abort(400)


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
            return jsonify({
                'user': current_user.to_dict(),
                'result': result,
            }), 200
        except:
            abort(400)


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
            return jsonify(current_user.to_dict()), 200
        except:
            abort(400)


@api.route('/users/profile/', methods=['POST'])
def edit_profile():
    try:
        data = request.get_json()

        current_user.name = data["name"]
        current_user.location = data["location"]
        current_user.bio = data["bio"]

        return jsonify({
            'user': current_user.to_dict(),
        }), 200
    except:
        abort(400)
