from flask import Blueprint, request, Response
from flask_jwt import jwt_required

from app.services import service_question
from app.shared.annotations import pagination, to_json

application_question = Blueprint("application_question", __name__)


@application_question.route("/")
def hello():
    return "hello question"


""" Responses lists """


@application_question.route("/add", methods=["POST"])
@jwt_required()
@to_json()
def add_question():
    label = request.form.get("label")
    response_uuid = request.form.get("response_uuid")

    return service_question.add(label, response_uuid)
