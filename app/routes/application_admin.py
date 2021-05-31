from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required

from app.services import service_crawler
from app.shared.annotations import has_role, pagination
from app.models import UserRole
from app.utils.utils_string import get_array_from_delimited_list

application_admin = Blueprint("application_admin", __name__)


@application_admin.route("/")
def hello():
    return "hello admin"


@application_admin.route("/crawl-artists", methods=["POST"])
@jwt_required
@has_role([UserRole.ADMIN])
def crawl_artists():
    genius_ids = get_array_from_delimited_list(
        request.form.get("genius_ids"), name="genius_ids"
    )

    try:
        genius_ids = [int(id_) for id_ in genius_ids]
    except Exception:
        abort(400, "Format of genius_ids is incorrect")

    for id_ in genius_ids:
        service_crawler.crawl_artist_full(id_)

    return Response(status=200)
