from flask import render_template
from flask_login import current_user, login_required

from app.models import Quiz, Product
from app.translate import translate


@translate.route('/translate/')
@login_required
def translate():
    words = "pater laetus est"
    words = words.split()

    return render_template(
        'translate.html',
        title="translate",
        words=words,
    )
