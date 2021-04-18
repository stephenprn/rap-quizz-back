from flask import abort
from typing import List

from app.shared.db import db

from app.repositories import ResponseRepository
from app.models import Response, ResponseType, Album, Artist, Song
from app.utils.utils_string import normalize_string
from app.utils.utils_query import FilterLabel

repo_response = ResponseRepository()

RESPONSES_LIST_SEARCH_TXT_NBR_RESULTS = 5

RESPONSE_TYPE_MODEL_MAP = {
    ResponseType.ALBUM: Album,
    ResponseType.ARTIST: Artist,
    ResponseType.SONG: Song,
}


def get_list_from_search_txt(
    search_txt: str, type_: ResponseType, responses_uuid_exclude: List[str]
) -> Response:
    search_txt = normalize_string(search_txt)
    return repo_response.list_(
        filter_search_text=search_txt,
        filter_type_in=[type_],
        filter_uuid_not_in=responses_uuid_exclude,
        nbr_results=RESPONSES_LIST_SEARCH_TXT_NBR_RESULTS,
    )


def add_simple(label: str, type_: ResponseType) -> Response:
    if (
        repo_response.get(
            filter_label=FilterLabel(label=label, ignore_case=True),
            filter_type_in=[type_],
        )
        != None
    ):
        abort(409, f"{type_} {label} already exists")

    model = RESPONSE_TYPE_MODEL_MAP.get(type_)

    if model == None:
        abort(400, f"No model associated to type {type_}")

    response = model(label)

    db.session.add(response)
    db.session.commit()

    return response


def add(response: Response):
    if (
        repo_response.get(
            filter_label=FilterLabel(label=response.label, ignore_case=True),
            filter_type_in=[response.type],
        )
        != None
    ):
        abort(409, f"{response.type} {response.label} already exists")

    db.session.add(response)
    db.session.commit()

    return response
