from datetime import datetime

from sqlalchemy import func

from .base_model import BaseModel
from app import db


class Score(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    score = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    attempt = db.Column(db.Integer)

    @classmethod
    def sum_by_day(cls):
        return db.session.query(cls.created_at, func.sum(cls.score)).group_by(func.date_format(cls.created_at, "%Y-%m-%d"))
