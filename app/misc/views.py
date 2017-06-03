from flask import render_template

from app.misc import misc


@misc.route('/terms')
def terms():
    return render_template(
        'misc/terms.html',
        title="LudoLatin  - Terms of Use",
    )


@misc.route('/privacy')
def privacy():
    return render_template(
        'misc/privacypolicy.html',
        title="LudoLatin  - Privacy Policy",
    )


@misc.route('/contact')
def contact():
    return render_template(
        'misc/contact.html',
        title="LudoLatin  - Contact",
    )


