from flask import render_template, redirect, request, url_for, session, current_app, flash
from flask_login import login_user, logout_user, current_user, login_required
from flask_principal import Identity, AnonymousIdentity, identity_changed
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetRequestForm, \
    PasswordResetForm, ChangeEmailForm
from app.models import User
from app.email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_by_email = User.query.filter_by(
            email=form.email.data
        ).first()
        user_by_username = User.query.filter_by(
            username=form.email.data
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
        title="Please sign in",
        form=form,
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
            current_user.follow(current_user)
            current_user.save()

            send_confirmation_email()

            return redirect(url_for('dashboard.dashboard'))
        # Register a new user
        else:
            user = User(
                email=form.email.data,
                username=form.username.data,
                password=form.password.data,
            ).save()
            user.follow(user)
            login_user(user.seen())

            # Flask-Principal: Create an Identity object and signal that the identity has changed,
            # which triggers on_identify_changed() and on_identify_loaded(). Identity() takes a unique ID.
            identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))

            return redirect(url_for('dashboard.dashboard'))

    return render_template(
        'auth/register.html',
        title="Register",
        form=form,
    )


@auth.route('/confirm')
@login_required
def resend_confirmation():
    if current_user.confirmed:
        flash('You have already confirmed your email address.', 'info')
    else:
        send_confirmation_email()
    return redirect(url_for('dashboard.dashboard'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('dashboard.dashboard'))
    if current_user.confirm(token):
        flash('You have confirmed your email address. Thanks!', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'danger')
        send_confirmation_email()
    return redirect(url_for('dashboard.dashboard'))


def send_confirmation_email():
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        'Confirm your email address',
        'auth/email/confirm',
        user=current_user,
        token=token,
    )
    flash('A confirmation link has been sent to you by email.', 'info')


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            current_user.save()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid password.', 'warning')
    return render_template(
        "auth/change_password.html",
        title="Change your password",
        form=form,
    )


@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect(url_for('dashboard.dashboard'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(
                user.email,
                'Reset your password',
                'auth/email/reset_password',
                user=user,
                token=token,
                next=request.args.get('next'),
            )
        flash('An email with instructions to reset your password has been sent to you.', 'info')
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/reset_password_request.html',
        title="Reset your password",
        form=form,
    )


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('dashboard.dashboard'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            flash('The password reset link is invalid or has expired, please tray again.', 'danger')
            return redirect(url_for('dashboard.dashboard'))

        user = User.query.get(data.get('reset'))

        if user is None:
            flash('The password reset link is invalid or has expired, please tray again.', 'danger')
            return redirect(url_for('dashboard.dashboard'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.', 'success')
            login_user(user.seen())
        return redirect(url_for('dashboard.dashboard'))

    return render_template(
        'auth/reset_password.html',
        title="Reset your password",
        form=form,
    )


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(
                new_email,
                'Confirm your new email address',
                'auth/email/change_email',
                user=current_user,
                token=token,
            )
            flash('An email with instructions to confirm your new email address has been sent to you.', 'info')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid email or password.', 'warning')
    return render_template(
        "auth/change_email.html",
        title="Change your email address",
        form=form,
    )


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.', 'success')
    else:
        flash('The link is invalid or has expired, please tray again.', 'danger')
    return redirect(url_for('dashboard.dashboard'))
