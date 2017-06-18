from flask import render_template, redirect, url_for, flash
from flask_login import current_user

from app.comments import comments
from app.comments.forms import CommentForm
from app.models import Comment


@comments.route('/comments/<int:post_id>', methods=['GET', 'POST'])
def comments(post_id):

    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            post_id=post_id,
            user_id=current_user.id,
        ).save()

        flash('Your comment has been published.')
        return redirect(url_for('comments.comments', post_id=post_id))

    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
    return render_template('comments.html', form=form, comments=comments)
