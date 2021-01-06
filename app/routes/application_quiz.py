from flask import Blueprint, request, Response, abort
from flask_jwt_extended import jwt_required

from app.services import service_quiz
from app.shared.annotations import pagination, to_json

application_quiz = Blueprint("application_quiz", __name__)


@application_quiz.route("/")
def hello():
    return "hello quiz"


""" Quizzes lists """


@application_quiz.route("/quizzes-list")
@pagination(20)
@to_json(paginated=True)
def get_quizzes_list(nbr_results: int, page_nbr: int):
    return service_quiz.get_quizzes_list(nbr_results, page_nbr)


""" Quizzes details """


@application_quiz.route("/generate-quiz")
@jwt_required
def generate_quiz():
    try:
        question_duration = int(request.args.get('question_duration'))
    except ValueError:
        abort(400, 'question_duration must be an integer')

    try:
        nbr_questions = int(request.args.get('nbr_questions'))
    except ValueError:
        abort(400, 'nbr_questions must be an integer')

    return service_quiz.generate_quiz(question_duration=question_duration, nbr_questions=nbr_questions)


@application_quiz.route("/join-quiz/<quiz_url>")
@jwt_required
@to_json()
def join_quiz(quiz_url: str):
    return service_quiz.join_quiz(quiz_url)
