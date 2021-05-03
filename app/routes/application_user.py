from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.services import service_user
from app.shared.annotations import pagination, to_json, has_role
from app.models import UserRole

application_user = Blueprint("application_user", __name__)


@application_user.route("/")
def hello():
    return "hello users"


""" Responses lists """


@application_user.route("/list")
@jwt_required
@has_role([UserRole.ADMIN])
@to_json(paginated=True)
@pagination(20)
def list_(nbr_results: int, page_nbr: int):
    return service_user.list_(nbr_results, page_nbr)
