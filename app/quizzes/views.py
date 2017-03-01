# -*- coding: utf-8 -*-

import datetime

from flask import render_template, redirect, request, url_for, make_response
from flask_login import current_user, login_required
from sqlalchemy.sql import * # Inefficient

from app.quizzes import quizzes
from app.quizzes.forms import QuizForm
from app.models import Answer, Sentence, Quiz, User, Score


def _get_user():
    return current_user if current_user.is_authenticated else None


@quizzes.route('/quiz/<int:id>/', methods=['GET', 'POST'])
@login_required
def ask(id):
    form = QuizForm()
    user = _get_user()

    # POST request:
    if form.validate_on_submit():

        # Retrieve the question_id from the cookie
        question_id = request.cookies.get('question_id')

        # Retrieve the question from the database
        # (passed to the model where used to determine correctness)
        question = Sentence.query.filter_by(id=question_id).first_or_404()

        # Retrieve the answer from the POST request data
        answer = form.answer.data

        # Save to the db via Answer model
        answer = Answer(answer, question, user).save()

        # Reload the page with a GET request
        response = make_response(
            redirect(url_for('quizzes.validate', id=id))
        )
        response.set_cookie('answer_id', str(answer.id))
        return response

    # If it wasn't a POST request, must be a GET, so we arrive here

    # Retrieve a random English phrase

    # All correctly answered sentences for the current quiz
    answered_sentences = Sentence.query.join(Sentence.answers, Answer.user).\
        filter(Sentence.quiz_id == id, Answer.is_correct == True, User.id == user.id).all()

    # All sentences for the current quiz
    all_sentences = Sentence.query.filter(Sentence.quiz_id == id).order_by(func.random()).all()

    # The set of unanswered questions
    # TODO: can we do this in a single DB query instead of the two above?
    questions = set(all_sentences) - set(answered_sentences)

    # If there are no unanswered questions, bump level
    if len(questions) == 0:

        # TODO: Redirect to a victory page instead
        return redirect(url_for('quizzes.victory', id=id))

    question = list(questions)[0]

    progress, unknown, quiz = template_setup(question, id)

    # Rather than returning `render_template`, build a response so that we can attach a cookie to it
    response = make_response(
        render_template(
            'quiz.html',
            question=question,
            unknown=unknown,
            form=form,
            progress=progress,
            quiz=quiz
        )
    )

    response.set_cookie('question_id', str(question.id))
    return response


@quizzes.route('/quiz/<int:id>/validate', methods=['GET'])
@login_required
def validate(id):
    form = QuizForm()

    # Retrieve the question_id from the cookie
    question_id = request.cookies.get('question_id')

    # Retrieve the answer from the cookie
    answer_id = request.cookies.get('answer_id')

    # Retrieve the question from the database
    # (passed to the model where used to determine correctness)
    question = Sentence.query.filter_by(id=question_id).first_or_404()

    # Retrieve the question from the database
    # (passed to the model where used to determine correctness)
    answer = Answer.query.filter_by(id=answer_id).first()

    progress, unknown, quiz = template_setup(question, id)

    # Rather than returning `render_template`, build a response so that we can attach a cookie to it
    return render_template(
        'quiz_validate.html',
        answer=answer,
        question=question,
        unknown=unknown,
        form=form,
        progress=progress,
        quiz=quiz,
    )


def template_setup(question, id):
    # Collection of correct answers previously given, returning just the `text` column
    correct = Answer.query.join(Sentence).with_entities(Answer.text).\
        filter(Answer.is_correct == True, Sentence.quiz_id == id, Answer.user == _get_user()).all()

    # Convert it to a list, and the list to a set
    correct = set([r for r, in correct])

    # True if the set (list of unique) latin translations is not in the set of correct answers
    unknown = not(Answer.query.join(Sentence).filter(
        Sentence.quiz_id == id,
        Answer.sentence == question,
        Answer.user == _get_user(),
        Answer.is_correct == True
    ).count())

    # The percentage of questions that have been answered correctly
    progress = float(len(correct)) / Sentence.query.filter_by(quiz_id=id).count() * 100

    quiz = Quiz.query.filter_by(id=id).first()

    return progress, unknown, quiz


@quizzes.route('/quiz/<int:id>/victory', methods=['GET'])
@login_required
def victory(id):
    user = _get_user()

    score = Sentence.query.filter_by(quiz_id=id).count() * 2
    neg_score = Answer.query.join(Sentence).filter(Answer.is_correct == False, Answer.user == user, Sentence.quiz_id == id).count()
    final_score = score - neg_score

    if user.quiz.id == id:
        user.total_score += final_score
        Score(score=final_score, user=user, quiz_id = id)
        user.quiz_id = id + 1

    daily = Score.\
        sum_by_day().\
        filter_by(user=_get_user()).\
        order_by(Score.created_at.desc()).\
        limit(7).\
        all()

    # remove the tuple wrappers
    daily = [i[0] for i in daily]
    # Pad to seven entries
    daily += [0] * (7 - len(daily))
    # most recent last
    daily.reverse()

    days = ['Tu',  'W', 'Th', 'F', 'Sa', 'Su', 'M']
    today = datetime.date.today().weekday()
    # Rotate the array so that today is last
    days = days[today:] + days[:today]

    return render_template(
        'quiz_victory.html',
        id=user.quiz_id,
        score=final_score,
        days=days,
        daily=daily
    )
