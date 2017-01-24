# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required, Length


class PhraseForm(FlaskForm):
    phrase = StringField(
        'Enter your translation', validators=[Required(), Length(1, 128)]
    )
    submit = SubmitField('Submit')
