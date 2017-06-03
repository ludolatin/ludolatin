from flask import render_template

from app.misc import misc


@misc.route('/beta')
def beta():
    return render_template(
        'misc/beta.html',
        title="LudoLatin  - We're building!",
    )


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


@misc.route('/robots.txt')
def robots():
    return render_template(
        'misc/robots.txt',
    )


@misc.route('/googleb362926a2c87791b.html')
def google_site_verification():
    return render_template(
        'misc/googleb362926a2c87791b.html',
    )
