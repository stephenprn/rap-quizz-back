from flask import abort
from typing import List

from app.shared.db import db

from app.repositories import QuestionRepository
from app.repositories import ResponseRepository
from app.models import (
    Question,
    QuestionResponse,
    QuestionResponseStatus,
    QuestionSubType,
)
from app.services.service_quiz import QUIZ_DEFAULT_NBR_RESPONSES

from app.utils.utils_query import FilterLabel
from app.utils.utils_string import check_length

repo_question = QuestionRepository()
repo_response = ResponseRepository()

RESPONSES_LIST_SEARCH_TXT_NBR_RESULTS = 5

LABEL_MIN_LENGTH = 8
LABEL_MAX_LENGTH = 100


def add(
    label: str, true_response_uuid: str, false_responses_uuid: List[str] = None
) -> Question:
    check_length(label, "Label", LABEL_MIN_LENGTH, LABEL_MAX_LENGTH)

    if true_response_uuid is None:
        abort(400, "True response must be specified through true_response_uuid")

    if true_response_uuid in false_responses_uuid:
        abort(400, "True response cannot be in false responses")

    if len(false_responses_uuid) + 1 > QUIZ_DEFAULT_NBR_RESPONSES:
        abort(
            400,
            f"A question can have a maximum of {QUIZ_DEFAULT_NBR_RESPONSES} responses",
        )

    if repo_question.get(filter_label=FilterLabel(label=label, ignore_case=True)):
        abort(409, "This question already exists")

    responses = repo_response.list_(
        filter_uuid_in=[true_response_uuid] + false_responses_uuid
    )

    true_response = next(
        (res for res in responses if res.uuid == true_response_uuid), None
    )
    false_responses = [res for res in responses if res.uuid in false_responses_uuid]

    if true_response == None:
        abort(404, "Right response specified does not exist")

    if len(false_responses) != len(false_responses_uuid):
        abort(
            404,
            f"{len(false_responses_uuid) - len(false_responses)} false responses specified were not found",
        )

    question = Question(label)
    question.type = true_response.type
    question.sub_type = QuestionSubType.UNKNOWN

    db.session.add(question)
    db.session.commit()

    question_response = QuestionResponse(
        question.id, true_response.id, QuestionResponseStatus.CORRECT
    )

    db.session.add(question_response)

    for res in false_responses:
        question_response = QuestionResponse(
            question.id, res.id, QuestionResponseStatus.WRONG
        )
        db.session.add(question_response)

    db.session.commit()

    return question


def list_(nbr_results: int, page_nbr: int, hidden: bool = None):
    return repo_question.list_(
        nbr_results=nbr_results,
        page_nbr=page_nbr,
        filter_hidden=hidden,
        load_full_response=True,
        with_nbr_results=True,
    )


def edit(question_uuid: str, hidden: bool = None, label: str = None):
    question = repo_question.get(filter_uuid_in=[question_uuid])

    if hidden is not None:
        question.hidden = hidden

    if label is not None:
        question.label = label

    db.session.add(question)
    db.session.commit()
