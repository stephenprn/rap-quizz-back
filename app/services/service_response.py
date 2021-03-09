from flask import abort

from app.shared.db import db
from app.shared.annotations import to_json

from app.repositories import ResponseRepository
from app.models import Response, ResponseType
from app.utils.utils_string import normalize_string

repo_response = ResponseRepository()

RESPONSES_LIST_SEARCH_TXT_NBR_RESULTS = 5


def get_list_from_search_txt(search_txt: str, type: ResponseType) -> Response:
    search_txt = normalize_string(search_txt)
    return repo_response.list_from_search_txt(
        search_txt, type, nbr_results=RESPONSES_LIST_SEARCH_TXT_NBR_RESULTS
    )


def add(label: str, type: ResponseType) -> Response:
    if repo_response.get(label, type) != None:
        abort(409, f"{type} {label} already exists")

    response = Response(label, type)

    db.session.add(response)
    db.session.commit()

    return response
