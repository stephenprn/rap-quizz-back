from flask import abort

from app.shared.db import db
from app.shared.annotations import to_json

from app.repositories import ResponseRepository
from app.models import Response, ResponseType
from app.utils.utils_string import normalize_string

repo = ResponseRepository()

RESPONSES_LIST_SEARCH_TXT_NBR_RESULTS = 5


@to_json()
def get_list_from_search_txt(search_txt: str, type: ResponseType):
    search_txt = normalize_string(search_txt)
    return repo.list_from_search_txt(
        search_txt, type, nbr_results=RESPONSES_LIST_SEARCH_TXT_NBR_RESULTS
    )


@to_json()
def add(label: str, type: ResponseType):
    # label_normalized = normalize_string(label)

    if repo.get(label, type) != None:
        abort(409, f"{type} {label} already exists")

    response = Response(label, type)

    db.session.add(response)
    db.session.commit()

    return response
