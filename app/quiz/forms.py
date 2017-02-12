# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class QuizForm(FlaskForm):
    answer = StringField('Enter your translation', validators=[DataRequired(), Length(1, 128)])
    submit = SubmitField('Submit')
