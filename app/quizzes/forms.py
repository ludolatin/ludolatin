# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length


class QuizForm(FlaskForm):
    answer = StringField(
        'Enter your translation',
        validators=[Length(1, 128, "Your translation was too short or too long.")]
    )
    submit = SubmitField('Check')
