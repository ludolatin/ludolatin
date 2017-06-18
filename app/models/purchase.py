from datetime import datetime

from ._base_model import BaseModel
from app import db

# user_item = db.Table(
#     'user_items',
#     db.Model.metadata,
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
#     db.Column('purchase_id', db.Integer, db.ForeignKey('purchase.id'), primary_key=True)
# )


class Purchase(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    price = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
