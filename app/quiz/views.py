# -*- coding: utf-8 -*-

import datetime

from flask import render_template, redirect, request, url_for, make_response
from flask_login import current_user, login_required
from sqlalchemy.sql import * # Inefficient

from app.quiz import quiz
from app.quiz.forms import QuizForm
from app.models import Answer, Sentence, Quiz, User, Score


def _get_user():
    return current_user if current_user.is_authenticated else None


@quiz.route('/quiz/<int:id>/', methods=['GET', 'POST'])
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

        last_answer = Answer.query.filter_by(user=user).order_by(Answer.id.desc()).first()

        attempt = request.cookies.get('attempt') or (last_answer.attempt + 1) if last_answer else 1


        # Save to the db via Answer model
        answer = Answer(answer, question, user, attempt).save()

        # Reload the page with a GET request
        response = make_response(
            redirect(url_for('quiz.validate', id=id))
        )
        response.set_cookie('answer_id', str(answer.id))
        response.set_cookie('attempt', str(attempt))

        return response

    attempt = request.cookies.get('attempt')

    # If it wasn't a POST request, must be a GET, so we arrive here
    current_quiz = Quiz.query.filter_by(id=id).first_or_404()

    # All correctly answered sentences for the current quiz
    answered_sentences = Sentence.query.join(Sentence.answers, Answer.user).\
        filter(Sentence.quiz_id == id, Answer.is_correct == True, User.id == user.id, Answer.attempt == attempt).all()

    # All sentences for the current quiz
    all_sentences = Sentence.query.filter(Sentence.quiz_id == id).order_by(func.random()).all()

    # The set of unanswered questions
    # TODO: can we do this in a single DB query instead of the two above?
    questions = set(all_sentences) - set(answered_sentences)

    # If there are no unanswered questions, bump level
    if len(questions) == 0:
        response = make_response(
            redirect(url_for('quiz.victory', id=id))
        )
        response.set_cookie('attempt', '', expires=0)
        return response

    question = list(questions)[0]
    progress, unknown = template_setup(question, id)

    # Rather than returning `render_template`, build a response so that we can attach a cookie to it
    response = make_response(
        render_template(
            'quiz.html',
            question=question,
            unknown=unknown,
            form=form,
            progress=progress,
            last_progress=progress,
            quiz=current_quiz
        )
    )

    response.set_cookie('question_id', str(question.id))
    return response


@quiz.route('/quiz/<int:id>/validate', methods=['GET'])
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

    progress, unknown = template_setup(question, id)

    quiz = Quiz.query.filter_by(id=id).first_or_404()

    # Get previous progress for progress bar animation
    if answer.is_correct:
        last_progress = float(len(correct_answers(id)) - 1) / Sentence.query.filter_by(quiz_id=id).count() * 100
    else:
        last_progress = progress

    # Rather than returning `render_template`, build a response so that we can attach a cookie to it
    return render_template(
        'quiz_validate.html',
        answer=answer,
        question=question,
        unknown=unknown,
        form=form,
        progress=progress,
        last_progress=last_progress,
        quiz=quiz,
    )


def correct_answers(id):
    attempt = request.cookies.get('attempt')

    # Collection of correct answers previously given, returning just the `text` column
    correct = Answer.query.join(Sentence).with_entities(Answer.text). \
        filter(Answer.is_correct == True, Sentence.quiz_id == id, Answer.user == _get_user(), Answer.attempt == attempt).all()
    # Convert it to a list, and the list to a set
    correct = set([r for r, in correct])
    return correct


def template_setup(question, id):
    correct = correct_answers(id)

    # The percentage of questions that have been answered correctly
    progress = float(len(correct)) / Sentence.query.filter_by(quiz_id=id).count() * 100

    # True if the set (list of unique) latin translations is not in the set of correct answers
    unknown = not(Answer.query.join(Sentence).filter(
        Sentence.quiz_id == id,
        Answer.sentence == question,
        Answer.user == _get_user(),
        Answer.is_correct == True
    ).count())

    return progress, unknown


@quiz.route('/quiz/<int:id>/victory', methods=['GET'])
@login_required
def victory(id):
    user = _get_user()

    last_attempt = Answer.query.filter_by(user=user).order_by(Answer.id.desc()).first().attempt
    last_score = Score.query.filter_by(user=user).order_by(Score.id.desc()).first()

    attempt = (last_score.attempt) if last_score else 0

    if last_attempt > attempt:
        score = Sentence.query.filter_by(quiz_id=id).count() * 2
        neg_score = Answer.query.join(Sentence) \
            .filter(Answer.is_correct == False, Answer.user == user, Sentence.quiz_id == id).count()
        final_score = score - neg_score

        user.total_score += final_score
        Score(score=final_score, user=user, quiz_id = id, attempt=last_attempt)
        user.quiz_id = id + 1
    else:
        return redirect(url_for('quiz.ask', id=user.quiz_id))

    daily = Score. \
        sum_by_day(). \
        filter_by(user=_get_user()). \
        order_by(Score.created_at.desc()). \
        limit(7). \
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

    quiz = Quiz.query.filter_by(id=user.quiz_id).first()
    current_topic = quiz.topic

    return render_template(
        'quiz_victory.html',
        id=user.quiz_id,
        score=final_score,
        days=days,
        daily=daily,
        current_topic=current_topic,
    )
