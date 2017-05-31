from flask import render_template, redirect, request, url_for
from flask_login import login_user, logout_user, current_user

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
        user_by_name = User.query.filter_by(
            username=form.email_or_username.data
        ).first()
        if user_by_email is not None and \
                user_by_email.verify_password(form.password.data):
            login_user(user_by_email.seen())
            return redirect(request.args.get('next') or url_for('dashboard.dashboard'))
        if user_by_name is not None and \
                user_by_name.verify_password(form.password.data):
            login_user(user_by_name.seen())
            return redirect(request.args.get('next') or url_for('dashboard.dashboard'))
    return render_template('login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('dashboard.dashboard'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    print "before form validated"
    if form.validate_on_submit():
        print "form validated"
        if current_user.is_authenticated:
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.password = form.password.data
            current_user.save()
            return redirect(url_for('dashboard.dashboard'))

        else:
            user = User(
                email=form.email.data,
                username=form.username.data,
                password=form.password.data,
            ).save()
            login_user(user)
            return redirect(url_for('quiz.ask', id=1))

    return render_template(
        'register.html',
        title="LudoLatin: Learn Latin for free",
        form=form)
