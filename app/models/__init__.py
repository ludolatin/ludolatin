from .base_model import BaseModel
from app import db

from .user import User
from .answer import Answer
from .topic import Topic
from .sentence import Sentence
from .quiz import Quiz
from .score import Score
from .product import Product
from .purchase import Purchase


class Language(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16))
    sentences = db.relationship('Sentence', backref='language')

    def __repr__(self):
        return '<Language: {0}>'.format(self.name)
