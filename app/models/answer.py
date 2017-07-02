import re
from datetime import datetime
from string import punctuation

from jellyfish import levenshtein_distance

from ._base_model import BaseModel
from app import db


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
        answer = punctuation_regex.sub('', unicode(text.lower().rstrip(" ")))

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
