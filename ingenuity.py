from os import environ

from flask import session
from app import create_app

app = create_app(environ.get('FLASK_ENV') or 'development')


@app.before_request
def make_session_permanent():
    session.permanent = True
