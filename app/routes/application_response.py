from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services import service_response
from app.shared.annotations import to_json
from app.models import ResponseType
from app.utils.utils_string import get_array_from_delimited_list

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
