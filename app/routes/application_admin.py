from flask import Blueprint, Response, request, abort
from flask_jwt_extended import jwt_required

from app.services import service_crawler
from app.shared.annotations import has_role
from app.models import UserRole
from app.utils.utils_string import get_array_from_delimited_list
from app.utils.utils_query import async_task

application_admin = Blueprint("application_admin", __name__)


@application_admin.route("/")
def hello():
    return "hello admin"


@application_admin.route("/crawl-artists", methods=["POST"])
@jwt_required
@has_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])
@async_task
def crawl_artists():
    genius_ids = get_array_from_delimited_list(
        request.form.get("genius_ids"), name="genius_ids"
    )

    try:
        genius_ids = [int(id_) for id_ in genius_ids]
    except Exception as e:
        print(e)
        abort(400, "Format of genius_ids is incorrect")

    for id_ in genius_ids:
        service_crawler.crawl_artist_full(id_)

    return Response(status=200)
