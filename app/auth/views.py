from flask import render_template, redirect, request, url_for, session, current_app
from flask_login import login_user, logout_user, current_user
from flask_principal import Identity, AnonymousIdentity, identity_changed

from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_by_email = User.query.filter_by(
            email=form.email_or_username.data
        ).first()
        user_by_username = User.query.filter_by(
            username=form.email_or_username.data
        ).first()

        user = user_by_email or user_by_username

        if user is not None and \
                user.verify_password(form.password.data):
            login_user(user.seen())

            # Flask-Principal: Create an Identity object and signal that the identity has changed,
            # which triggers on_identify_changed() and on_identify_loaded(). Identity() takes a unique ID.
            identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))

            return redirect(request.args.get('next') or url_for('dashboard.dashboard'))

    return render_template(
        'auth/login.html',
        title="LudoLatin - Sign in",
        form=form
    )


@auth.route('/logout')
def logout():
    logout_user()

    # Flask-Principal: Remove session keys
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    # Flask-Principal: the user is now anonymous
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())

    return redirect(url_for('dashboard.dashboard'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        # Register an existing guest user # TODO: What about a registered user visiting the registration form?
        if current_user.is_authenticated:
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.password = form.password.data
            current_user.save()
            return redirect(url_for('dashboard.dashboard'))
        # Register a new user
        else:
            user = User(
                email=form.email.data,
                username=form.username.data,
                password=form.password.data,
            ).save()
            login_user(user)

            # Flask-Principal: Create an Identity object and signal that the identity has changed,
            # which triggers on_identify_changed() and on_identify_loaded(). Identity() takes a unique ID.
            identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))

            return redirect(url_for('dashboard.dashboard'))

    return render_template(
        'auth/register.html',
        title="LudoLatin - Register",
        form=form)
