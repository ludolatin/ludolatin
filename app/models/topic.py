from .base_model import BaseModel
from app import db


class Topic(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    quizzes = db.relationship('Quiz', backref='topic')
    name = db.Column(db.String(32))
    text = db.Column(db.Text)

    def __repr__(self):
        return '<Topic: {0}>'.format(self.name)
