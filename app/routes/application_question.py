from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required

from app.services import service_question
from app.shared.annotations import pagination, to_json, has_role
from app.models import UserRole

application_question = Blueprint("application_question", __name__)


@application_question.route("/")
def hello():
    return "hello question"


""" Responses lists """


@application_question.route("/add", methods=["POST"])
@jwt_required
@to_json()
def add_question():
    label = request.form.get("label")
    response_uuid = request.form.get("response_uuid")

    return service_question.add(label, response_uuid)


@application_question.route("/list")
@jwt_required
@has_role([UserRole.ADMIN])
@to_json(paginated=True)
@pagination(20)
def list_questions(nbr_results: int, page_nbr: int):
    return service_question.list_(nbr_results, page_nbr)


@application_question.route("/hide/<question_uuid>")
@jwt_required
@has_role([UserRole.ADMIN])
def hide(question_uuid: str):
    try:
        hidden = bool(request.args.get("hidden"))
    except ValueError:
        abort(400, "hidden must be an boolean")

    service_question.hide(question_uuid, hidden)

    return Response(status=200)