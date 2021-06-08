from flask import Blueprint, Response, request, json
from flask_jwt_extended import jwt_required

from app.services import service_artist, service_question_generator
from app.shared.annotations import has_role, pagination, to_json
from app.models import UserRole
from app.utils.utils_string import get_array_from_delimited_list

application_artist = Blueprint("application_artist", __name__)


@application_artist.route("/")
def hello():
    return "hello admin"


@application_artist.route("/list")
@jwt_required
@has_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])
@pagination(20)
@to_json(True)
def list_artists(nbr_results: int, page_nbr: int):
    return service_artist.get_artists_list(nbr_results, page_nbr)


@application_artist.route("/generate-questions", methods=["POST"])
@jwt_required
@has_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])
def generate_questions():
    artist_uuid = request.json.get("artist_uuid")

    nbr_generated = service_question_generator.generate_questions_artist(
        artist_uuid=artist_uuid
    )

    return json.dumps({"nbr_generated": nbr_generated})
