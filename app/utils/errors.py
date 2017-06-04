from flask import request, render_template

from . import utils
from .. import api


@utils.app_errorhandler(403)
def forbidden(error):
    if request.path.startswith('/api'):
        return api.errors.forbidden(error)
    return render_template('error/403.html', title="LudoLatin - Forbidden"), 403


@utils.app_errorhandler(404)
def page_not_found(error):
    if request.path.startswith('/api'):
        return api.errors.not_found(error)
    return render_template('error/404.html', title="LudoLatin - Not found"), 404


@utils.app_errorhandler(500)
def internal_server_error(error):
    if request.path.startswith('/api'):
        return api.errors.internal_server_error(error)
    return render_template('error/500.html', title="LudoLatin - Server error"), 500
