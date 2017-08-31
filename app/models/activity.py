from datetime import datetime

from app import db
from ._base_model import BaseModel


class Activity(db.Model, BaseModel):
    __tablename__ = 'activity'
    id = db.Column(db.Integer, primary_key=True)
    body_html = db.Column(db.Text)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    public = db.Column(db.Boolean)
