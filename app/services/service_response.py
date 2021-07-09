from flask import abort
from typing import List

from app.shared.db import db

from app.repositories import ResponseRepository
from app.models import Response, ResponseType, Album, Artist, Song
from app.utils.utils_string import normalize_string, check_length
from app.utils.utils_query import FilterText

repo_response = ResponseRepository()

RESPONSES_LIST_SEARCH_TXT_NBR_RESULTS = 5

RESPONSE_LABEL_MIN_LENGTH = 1
RESPONSE_LABEL_MAX_LENGTH = 128

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
        filter_label=FilterText(
            text=search_txt,
            ignore_case=True,
            partial_match=True),
        filter_type_in=[type_],
        filter_uuid_not_in=responses_uuid_exclude,
        nbr_results=RESPONSES_LIST_SEARCH_TXT_NBR_RESULTS,
    )


def add_simple(label: str, type_: ResponseType) -> Response:
    label = label.lower().strip()
    check_length(
        label,
        "label",
        min_length=RESPONSE_LABEL_MIN_LENGTH,
        max_length=RESPONSE_LABEL_MAX_LENGTH,
    )

    if (
        repo_response.get(
            filter_label=FilterText(text=label, ignore_case=True),
            filter_type_in=[type_],
        )
        is not None
    ):
        abort(409, f"{type_} {label} already exists")

    model = RESPONSE_TYPE_MODEL_MAP.get(type_)

    if model is None:
        abort(400, f"This type is invalid: {type_}")

    response = model(label)

    db.session.add(response)
    db.session.commit()

    return response


def add(response: Response):
    response.label = response.label.strip()
    check_length(
        response.label,
        "label",
        min_length=RESPONSE_LABEL_MIN_LENGTH,
        max_length=RESPONSE_LABEL_MAX_LENGTH,
    )

    if (
        repo_response.get(
            filter_label=FilterText(text=response.label, ignore_case=True),
            filter_type_in=[response.type],
        )
        is not None
    ):
        abort(409, f"{response.type} {response.label} already exists")

    db.session.add(response)
    db.session.commit()

    return response


def list_(nbr_results: int, page_nbr: int, hidden: bool = None):
    return repo_response.list_(
        nbr_results=nbr_results,
        page_nbr=page_nbr,
        filter_hidden=hidden,
        with_nbr_results=True,
        order_update_date=False,
    )


def edit(response_uuid: str, hidden: bool = None, label: str = None):
    response = repo_response.get(filter_uuid_in=[response_uuid])

    if response is None:
        abort(404, "Response not found")

    if label is not None:
        label = label.lower().strip()
        check_length(
            label,
            "label",
            min_length=RESPONSE_LABEL_MIN_LENGTH,
            max_length=RESPONSE_LABEL_MAX_LENGTH,
        )
        response.label = label

    if hidden is not None:
        response.hidden = hidden

    db.session.add(response)
    db.session.commit()

    return response
