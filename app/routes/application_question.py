from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required

from app.services import service_question
from app.shared.annotations import pagination, to_json, has_role
from app.models import UserRole
from app.utils.utils_string import get_array_from_delimited_list

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
    true_response_uuid = request.form.get("true_response_uuid")
    false_responses_uuid = get_array_from_delimited_list(
        request.form.get("false_responses_uuid"), name="false_responses_uuid"
    )

    return service_question.add(label=label, true_response_uuid=true_response_uuid, false_responses_uuid=false_responses_uuid)


@application_question.route("/list")
@jwt_required
@has_role([UserRole.ADMIN])
@to_json(paginated=True)
@pagination(20)
def list_questions(nbr_results: int, page_nbr: int):
    return service_question.list_(nbr_results, page_nbr)


@application_question.route("/edit/<question_uuid>", methods=["POST"])
@jwt_required
@has_role([UserRole.ADMIN])
def edit(question_uuid: str):
    if request.form.get("hidden") != None:
        try:
            hidden = bool(request.form.get("hidden"))
        except ValueError:
            abort(
                400,
                f"hidden must be an boolean, received: {request.form.get('hidden')}",
            )
    else:
        hidden = None

    if request.form.get("label") != None:
        label = request.form.get("label")
    else:
        label = None

    if request.form.get("true_response_uuid") != None:
        true_response_uuid = request.form.get("true_response_uuid")
    else:
        true_response_uuid = None

    if request.form.get("false_responses_uuid") != None:
        false_responses_uuid = get_array_from_delimited_list(
            request.form.get("false_responses_uuid"), name="false_responses_uuid"
        )
    else:
        false_responses_uuid = None

    service_question.edit(question_uuid, hidden=hidden, label=label,
                          true_response_uuid=true_response_uuid, false_responses_uuid=false_responses_uuid)

    return Response(status=200)


@application_question.route("/<question_uuid>")
@jwt_required
@has_role([UserRole.ADMIN])
@to_json()
def get_question(question_uuid: str):
    return service_question.get(question_uuid)
