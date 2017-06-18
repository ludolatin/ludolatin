from flask_login import current_user
from ._base_model import BaseModel
from app import db


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


def streak_recovery_availability(product):
    if product.total_price == 0 or current_user.total_score < product.total_price:
        return False
    else:
        return True
