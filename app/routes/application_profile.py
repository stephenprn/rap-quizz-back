from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.services import service_profile
from app.shared.annotations import pagination, to_json

application_profile = Blueprint("application_profile", __name__)


@application_profile.route("/")
def hello():
    return "hello profile"


@application_profile.route("/history")
@jwt_required
@pagination(20)
@to_json(True)
def get_history(nbr_results: int, page_nbr: int):
    return service_profile.get_history(nbr_results, page_nbr)
