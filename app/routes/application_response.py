from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required

from app.services import service_response
from app.shared.annotations import pagination, to_json, has_role
from app.models import ResponseType, UserRole
from app.utils.utils_string import get_array_from_delimited_list, to_bool

application_response = Blueprint("application_response", __name__)


@application_response.route("/")
def hello():
    return "hello response"


""" Responses lists """


@application_response.route("/search")
@jwt_required
@to_json()
def get_list_from_search_txt():
    search_txt = request.args.get("search_txt")
    type_ = request.args.get("type")
    responses_uuid_exclude = get_array_from_delimited_list(
        request.args.get("responses_uuid_exclude"), name="responses_uuid_exclude"
    )

    return service_response.get_list_from_search_txt(
        search_txt, type_, responses_uuid_exclude
    )


@application_response.route("/add", methods=["POST"])
@jwt_required
@to_json()
def add_response():
    label = request.form.get("label")
    type_ = request.form.get("type")

    return service_response.add_simple(label, ResponseType[type_])


@application_response.route("/edit/<response_uuid>", methods=["POST"])
@jwt_required
@has_role([UserRole.ADMIN])
def edit(response_uuid: str):
    if request.form.get("hidden") != None:
        try:
            hidden = to_bool(request.form.get("hidden"))
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

    service_response.edit(response_uuid, hidden=hidden, label=label)

    return Response(status=200)


@application_response.route("/list")
@jwt_required
@has_role([UserRole.ADMIN])
@to_json(paginated=True)
@pagination(20)
def list_questions(nbr_results: int, page_nbr: int):
    return service_response.list_(nbr_results, page_nbr)
