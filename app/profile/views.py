from flask import render_template
from flask_login import current_user

from app.models import User
from app.profile import profile


@profile.route('/users/<username>/')
def view(username):
    user = User.query.filter_by(username=username).first()
    return render_template(
        'profile/profile.html',
        title="profile",
        user=user,
    )


@profile.route('/users/edit/')
def edit():
    return render_template(
        'profile/profile_edit.html',
        title="profile",
    )
