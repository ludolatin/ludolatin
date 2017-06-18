from ._base_model import BaseModel
from app import db


class Quiz(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    sentences = db.relationship('Sentence', backref='quiz')
    name = db.Column(db.String(32))
    users = db.relationship('User', backref='quiz')
    scores = db.relationship('Score', backref='quiz')
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))

    def __repr__(self):
        return '<Quiz: {0}>'.format(self.name)
