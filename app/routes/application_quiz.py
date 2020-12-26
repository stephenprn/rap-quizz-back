from flask import Blueprint, request, Response
from flask_jwt import jwt_required

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
@jwt_required()
def generate_quiz():
    return service_quiz.generate_quiz()


@application_quiz.route("/join-quiz/<quiz_url>")
@jwt_required()
def join_quiz(quiz_url: str):
    return service_quiz.join_quiz(quiz_url)


@application_quiz.route("/answer-response/<quiz_url>", methods=["POST"])
@jwt_required()
def answer_reponse(quiz_url: str):
    try:
        question_index = int(request.form.get("question_index"))
    except Exception:
        abort(400, "Question index invalid")

    question_uuid = request.form.get("question_uuid")
    response_uuid = request.form.get("response_uuid")

    return service_quiz.answer_reponse(
        quiz_url, question_index, question_uuid, response_uuid
    )
