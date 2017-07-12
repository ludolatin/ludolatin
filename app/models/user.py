import re
import hashlib
from datetime import datetime

from flask import url_for, current_app, request
from flask_login import UserMixin
from sqlalchemy.orm import synonym
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from ._base_model import BaseModel
from .score import Score
from app import db


EMAIL_REGEX = re.compile(r'^\S+@\S+\.\S+$')
USERNAME_REGEX = re.compile(r'^\S+$')


def check_length(attribute, length):
    # Checks the attribute's length.
    try:
        return bool(attribute) and len(attribute) <= length
    except:
        return False


class User(UserMixin, db.Model, BaseModel):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    _username = db.Column('username', db.String(64), unique=True)
    _email = db.Column('email', db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), default=1)
    total_score = db.Column(db.Integer, default=0)
    scores = db.relationship('Score', backref='user')
    purchases = db.relationship('Purchase', backref='user')
    streak_start_date = db.Column(db.DateTime)
    answers = db.relationship('Answer', backref='user')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    confirmed = db.Column(db.Boolean, default=False)
    profile_picture = db.Column(db.Integer, default=1)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        if self.is_admin:
            return '<Admin: {0}>'.format(self.username)
        return '<User: {0}>'.format(self.username)

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        is_valid_length = check_length(username, 64)
        if not is_valid_length or not bool(USERNAME_REGEX.match(username)):
            raise ValueError('{} is not a valid username'.format(username))
        self._username = username

    username = synonym('_username', descriptor=username)

    # Flask-Blogging
    def get_name(self):
        return self.username

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        if not check_length(email, 64) or not bool(EMAIL_REGEX.match(email)):
            raise ValueError('{} is not a valid email address'.format(email))
        self._email = email

    email = synonym('_email', descriptor=email)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        if not bool(password):
            raise ValueError('no password given')

        hashed_password = generate_password_hash(password)
        if not check_length(hashed_password, 128):
            raise ValueError('not a valid password, hash is too long')
        self.password_hash = hashed_password

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def seen(self):
        self.last_seen = datetime.utcnow()
        return self.save()

    def promote_to_admin(self):
        self.is_admin = True
        return self.save()

    def to_dict(self):
        return {
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'total_score': self.total_score,
            'streak': self.streak,
            'profile_picture': self.profile_picture,
            'user_url': url_for(
                'api.get_user', id=self.id, _external=True
            ),
        }

    @property
    def last_score_age(self):
        last_score = Score.query.filter_by(user=self).order_by(Score.created_at.desc()).first()
        last_score_age = (datetime.utcnow() - last_score.created_at) if last_score else None
        last_score_age = last_score_age.days * 24 + last_score_age.seconds / 3600 if last_score_age else None
        return last_score_age

    @property
    def streak(self):
        if self.streak_start_date and self.last_score_age < 36:
            return (datetime.utcnow() - self.streak_start_date).days
        else:
            return 0

    @property
    def rank(self):
        return User.query.filter(self.total_score < User.total_score).count() + 1

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        self.save()
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        self.save()
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.save()
        return True


