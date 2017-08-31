from flask import render_template
from flask_login import current_user

from app.activity import activity
from app.models import User, Activity


@activity.route('/activity/')
def activity():
    activity = []
    for user in current_user.following:
        if user.activity:
            for item in user.activity.all():
                if item.public:
                    activity.append(item)

    activity.reverse()

    return render_template(
        'activity.html',
        title="Store",
        activity=activity,
    )
