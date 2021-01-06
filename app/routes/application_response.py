from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required

from app.services import service_response
from app.shared.annotations import pagination, to_json

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
    type = request.args.get("type")

    return service_response.get_list_from_search_txt(search_txt, type)


@application_response.route("/add", methods=["POST"])
@jwt_required
@to_json()
def add_response():
    label = request.form.get("label")
    type = request.form.get("type")

    return service_response.add(label, type)
