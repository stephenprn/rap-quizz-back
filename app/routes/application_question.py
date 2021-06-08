from flask import Blueprint, request, Response, abort
from flask_jwt_extended import jwt_required

from app.services import service_question
from app.shared.annotations import pagination, to_json, has_role
from app.models import UserRole, ResponseType
from app.utils.utils_string import get_array_from_delimited_list, to_bool

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

    if request.form.get("response_type") is not None:
        try:
            response_type = ResponseType[request.form.get("response_type")]
        except Exception:
            abort(
                400,
                f'Invalid response type: {request.form.get("response_type")}')
    else:
        response_type = None

    true_response_uuid = request.form.get("true_response_uuid")
    false_responses_uuid = get_array_from_delimited_list(
        request.form.get("false_responses_uuid"), name="false_responses_uuid"
    )
    ranked_responses_uuid = get_array_from_delimited_list(
        request.form.get("ranked_responses_uuid"), name="ranked_responses_uuid"
    )
    year = request.form.get("year")
    ranking = to_bool(request.form.get("ranking"))

    return service_question.add(
        label,
        response_type,
        ranking,
        true_response_uuid=true_response_uuid,
        false_responses_uuid=false_responses_uuid,
        ranked_responses_uuid=ranked_responses_uuid,
        year=year,
    )


@application_question.route("/list")
@jwt_required
@has_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])
@to_json(paginated=True)
@pagination(20)
def list_questions(nbr_results: int, page_nbr: int):
    return service_question.list_(nbr_results, page_nbr)


@application_question.route("/edit/<question_uuid>", methods=["POST"])
@jwt_required
@has_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])
def edit(question_uuid: str):
    if request.form.get("hidden") is not None:
        try:
            hidden = to_bool(request.form.get("hidden"))
        except ValueError:
            abort(
                400,
                f"hidden must be an boolean, received: {request.form.get('hidden')}",
            )
    else:
        hidden = None

    if request.form.get("response_type") is not None:
        try:
            response_type = ResponseType[request.form.get("response_type")]
        except Exception:
            abort(
                400,
                f'Invalid response type: {request.form.get("response_type")}')
    else:
        response_type = None

    if request.form.get("label") is not None:
        label = request.form.get("label")
    else:
        label = None

    if request.form.get("true_response_uuid") is not None:
        true_response_uuid = request.form.get("true_response_uuid")
    else:
        true_response_uuid = None

    if request.form.get("false_responses_uuid") is not None:
        false_responses_uuid = get_array_from_delimited_list(
            request.form.get("false_responses_uuid"), name="false_responses_uuid")
    else:
        false_responses_uuid = None

    if request.form.get("ranked_responses_uuid") is not None:
        ranked_responses_uuid = get_array_from_delimited_list(
            request.form.get("ranked_responses_uuid"), name="ranked_responses_uuid")
    else:
        ranked_responses_uuid = None

    year = request.form.get("year")

    if request.form.get("ranking") is not None:
        try:
            ranking = to_bool(request.form.get("ranking"))
        except ValueError:
            abort(
                400,
                f"ranking must be an boolean, received: {request.form.get('ranking')}",
            )
    else:
        ranking = None

    service_question.edit(
        question_uuid,
        hidden=hidden,
        ranking=ranking,
        label=label,
        true_response_uuid=true_response_uuid,
        false_responses_uuid=false_responses_uuid,
        ranked_responses_uuid=ranked_responses_uuid,
        response_type=response_type,
        year=year,
    )

    return Response(status=200)


@application_question.route("/<question_uuid>")
@jwt_required
@has_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])
@to_json()
def get_question(question_uuid: str):
    return service_question.get(question_uuid)
