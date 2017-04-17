import datetime

from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required

from app.topic import topic
from app.models import Topic


def _get_user():
    return current_user if current_user.is_authenticated else None


@topic.route('/topic/<int:id>')
@login_required
def topic(id):
    user = _get_user()

    topic = Topic.query.filter_by(id=id).first_or_404()

    return render_template(
        'topic.html',
        topic=topic
    )
