from ._base_model import BaseModel
from app import db

sentence_to_sentence = db.Table(
    'sentence_to_sentence',
    db.Model.metadata,
    db.Column('left_sentence_id', db.Integer, db.ForeignKey('sentence.id'), primary_key=True),
    db.Column('right_sentence_id', db.Integer, db.ForeignKey('sentence.id'), primary_key=True)
)


class Sentence(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128))
    answers = db.relationship('Answer', backref='sentence')
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    type = db.Column(db.String(16))

    translations = db.relationship(
        "Sentence",
        secondary=sentence_to_sentence,
        primaryjoin=id == sentence_to_sentence.c.left_sentence_id,
        secondaryjoin=id == sentence_to_sentence.c.right_sentence_id,
        backref=db.backref("back_translations"),
    )

    def __repr__(self):
        return '<Sentence: {0}>'.format(self.text)
