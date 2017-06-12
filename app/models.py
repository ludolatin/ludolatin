import re
from datetime import datetime
from string import punctuation

from flask import url_for
from flask_login import UserMixin, current_user
from jellyfish import levenshtein_distance
from sqlalchemy import func
from sqlalchemy.orm import synonym
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


EMAIL_REGEX = re.compile(r'^\S+@\S+\.\S+$')
USERNAME_REGEX = re.compile(r'^\S+$')


def check_length(attribute, length):
    # Checks the attribute's length.
    try:
        return bool(attribute) and len(attribute) <= length
    except:
        return False


class BaseModel:
    # Base for all models, providing save, delete and from_dict methods.

    def __commit(self):
        # Commits the current db.session, does rollback on failure.
        from sqlalchemy.exc import IntegrityError
        try:
            db.session.commit()
        except IntegrityError, e:
            print "DATABASE INTEGRITY ERROR:", e, "rolling back."
            db.session.rollback()

    def delete(self):
        # Deletes this model from the db (through db.session)
        db.session.delete(self)
        self.__commit()

    def save(self):
        # Adds this model to the db (through db.session)
        db.session.add(self)
        self.__commit()
        return self

    @classmethod
    def count_by_hour(cls, column):
        return db.session.query(func.count(column)).group_by(func.date_format(column, "%Y-%m-%d %H"))

    @classmethod
    def count_by_day(cls, column):
        return db.session.query(func.count(column)).group_by(func.date_format(column, "%Y-%m-%d"))

    @classmethod
    def from_dict(cls, model_dict):
        return cls(**model_dict).save()


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


class Answer(db.Model, BaseModel):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_correct = db.Column(db.Boolean, default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sentence_id = db.Column(db.Integer, db.ForeignKey('sentence.id'))
    attempt = db.Column(db.Integer)

    def __init__(self, text=None, sentence=None, user=None, attempt=0, created_at=None):

        # Is the submitted answer correct?
        is_correct = False  # Incorrect
        punctuation_regex = re.compile('[%s]' % re.escape(punctuation))
        answer = punctuation_regex.sub('', unicode(text.lower()))

        if sentence is not None:
            for translation in sentence.translations:
                if answer == punctuation_regex.sub('', unicode(translation.text.lower())):
                    is_correct = True  # Correct
                    break

        if sentence is not None and not is_correct:
            for translation in sentence.translations:
                if levenshtein_distance(
                        answer,
                        punctuation_regex.sub('', unicode(translation.text.lower()))
                ) == 1:
                    is_correct = None  # Typo
                    break

        self.text = text
        self.sentence_id = sentence.id if sentence else None
        self.is_correct = is_correct
        self.user = user
        self.created_at = created_at or datetime.utcnow()
        self.attempt = attempt

    def __repr__(self):
        return '<{0} answer: {1} by {2}>'.format(self.status, self.text, self.user or 'None')

    @property
    def status(self):
        if self.is_correct:
            return 'Correct'
        elif self.is_correct is None:
            return 'Typo'
        else:
            return 'Incorrect'

    def correct(self):
        self.is_correct = True
        self.save()


sentence_to_sentence = db.Table(
    'sentence_to_sentence',
    db.Model.metadata,
    db.Column('left_sentence_id', db.Integer, db.ForeignKey('sentence.id'), primary_key=True),
    db.Column('right_sentence_id', db.Integer, db.ForeignKey('sentence.id'), primary_key=True)
)


class Sentence(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128))
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    answers = db.relationship('Answer', backref='sentence')
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))

    translations = db.relationship(
        "Sentence",
        secondary=sentence_to_sentence,
        primaryjoin=id == sentence_to_sentence.c.left_sentence_id,
        secondaryjoin=id == sentence_to_sentence.c.right_sentence_id,
        backref=db.backref("back_translations"),
    )

    def __repr__(self):
        return '<Sentence: {0}>'.format(self.text)


class Language(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16))
    sentences = db.relationship('Sentence', backref='language')

    def __repr__(self):
        return '<Language: {0}>'.format(self.name)


class Topic(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    quizzes = db.relationship('Quiz', backref='topic')
    name = db.Column(db.String(32))
    text = db.Column(db.Text)

    def __repr__(self):
        return '<Topic: {0}>'.format(self.name)


class Quiz(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    sentences = db.relationship('Sentence', backref='quiz')
    name = db.Column(db.String(32))
    users = db.relationship('User', backref='quiz')
    scores = db.relationship('Score', backref='quiz')
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))

    def __repr__(self):
        return '<Quiz: {0}>'.format(self.name)


class Score(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    score = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    attempt = db.Column(db.Integer)

    @classmethod
    def sum_by_day(cls):
        return db.session.query(func.sum(cls.score)).group_by(func.date_format(cls.created_at, "%Y-%m-%d"))

    def __repr__(self):
        return '<Score: {0}>'.format(self.score)

    def to_dict(self):
        return {
            'created_at': self.created_at,
            'score': self.score,
            'user_id': self.user_id,
        }


user_item = db.Table(
    'user_items',
    db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('purchase_id', db.Integer, db.ForeignKey('purchase.id'), primary_key=True)
)


def streak_recovery_availability(product):
    if product.total_price == 0 or current_user.total_score < product.total_price:
        return False
    else:
        return True


class Product(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    description = db.Column(db.String(128))
    price = db.Column(db.String(16))
    purchases = db.relationship('Purchase', backref='product')
    pricing_formula = db.Column(db.String(256))
    availability_function = db.Column(db.String(256))

    def __repr__(self):
        return '<Product: {0}>'.format(self.name)

    @property
    def total_price(self):
        return eval(self.pricing_formula)

    @property
    def available(self):
        return eval(self.availability_function)


class Purchase(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    price = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
