from flask import Blueprint, Response
from flask_jwt_extended import jwt_required

from app.services import service_crawler
from app.shared.annotations import has_role

application_admin = Blueprint("application_admin", __name__)


@application_profile.route("/")
def hello():
    return "hello admin"


@application_admin.route("/crawl-artist/<genius_id>")
@jwt_required
@has_role([UserRole.ADMIN])
def get_history(genius_id: str):
    try:
        genius_id = int(genius_id)
    except Exception:
        abort(400, f"Bad format for genius id: {genius_id}")

    service_crawler.crawl_artist_full(genius_id)

    return Response(status=200)
