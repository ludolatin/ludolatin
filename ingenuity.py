from flask import session
from app import create_app

app = create_app('development')


@app.before_request
def make_session_permanent():
    session.permanent = True
    print session