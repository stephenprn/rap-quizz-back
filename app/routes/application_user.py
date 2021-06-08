from flask import Blueprint, request, abort, Response
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
@has_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])
@to_json(paginated=True)
@pagination(20)
def list_(nbr_results: int, page_nbr: int):
    return service_user.list_(nbr_results, page_nbr)


@application_user.route("/edit/<user_uuid>", methods=["POST"])
@jwt_required
@has_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])
def edit(user_uuid: str):
    if request.form.get("role") is not None:
        try:
            role = UserRole[request.form.get("role")]
        except Exception:
            abort(400, f'Invalid user role: {request.form.get("role")}')
    else:
        role = None

    service_user.edit(
        user_uuid,
        role=role,
    )

    return Response(status=200)
