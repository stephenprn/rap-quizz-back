from flask import abort
from typing import List, Optional

from app.shared.db import db

from app.repositories import QuestionRepository
from app.repositories import ResponseRepository
from app.models import (
    Question,
    QuestionResponse,
    QuestionResponseStatus,
    QuestionSubType,
    ResponseType,
)
from app.services.service_quiz import QUIZ_DEFAULT_NBR_RESPONSES

from app.utils.utils_query import FilterLabel
from app.utils.utils_string import check_length

repo_question = QuestionRepository()
repo_response = ResponseRepository()

RESPONSES_LIST_SEARCH_TXT_NBR_RESULTS = 5

LABEL_MIN_LENGTH = 8
LABEL_MAX_LENGTH = 100

YEAR_MIN = 1900
YEAR_MAX = 2100


def add(
    label: str,
    response_type: ResponseType,
    true_response_uuid: str,
    false_responses_uuid: List[str] = None,
    year: str = None,
) -> Question:
    check_length(label, "Label", LABEL_MIN_LENGTH, LABEL_MAX_LENGTH)

    if not response_type.is_precise and true_response_uuid is None:
        abort(400, "True response must be specified through true_response_uuid")

    if not response_type.is_precise and true_response_uuid in false_responses_uuid:
        abort(400, "True response cannot be in false responses")

    if (
        not response_type.is_precise
        and len(false_responses_uuid) + 1 > QUIZ_DEFAULT_NBR_RESPONSES
    ):
        abort(
            400,
            f"A question can have a maximum of {QUIZ_DEFAULT_NBR_RESPONSES} responses",
        )

    if response_type.is_precise:
        if not year:
            abort(400, "Year must be specified")

        try:
            int(year)
        except Exception:
            abort(400, "Year must be an int")

        if int(year) > YEAR_MAX or int(year) < YEAR_MIN:
            abort(400, f"Year must be between {YEAR_MIN} and {YEAR_MAX}")

    if repo_question.get(filter_label=FilterLabel(label=label, ignore_case=True)):
        abort(409, "This question already exists")

    if not response_type.is_precise:
        responses = repo_response.list_(
            filter_uuid_in=[true_response_uuid] + false_responses_uuid
        )

        if any([r.type != response_type for r in responses]):
            abort(
                400,
                f"Responses specified must be the same type as the question type: {response_type}",
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
    question.type = response_type
    question.sub_type = QuestionSubType.UNKNOWN

    if response_type.is_precise:
        question.response_precise = year

    db.session.add(question)
    db.session.commit()

    if response_type.is_precise:
        return question

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
        order_update_date=False,
    )


def get(question_uuid: str):
    question = repo_question.get(
        filter_uuid_in=[question_uuid],
        load_full_response=True,
    )

    if not question:
        abort(404, "Question not found")

    return question


def edit(
    question_uuid: str,
    hidden: bool = None,
    label: str = None,
    response_type: Optional[ResponseType] = None,
    true_response_uuid: Optional[str] = None,
    false_responses_uuid: Optional[List[str]] = None,
    year: str = None,
):
    question = repo_question.get(
        filter_uuid_in=[question_uuid],
        load_full_response=True,
    )

    if question is None:
        abort(404, "Question not found")

    if label is not None:
        check_length(label, "Label", LABEL_MIN_LENGTH, LABEL_MAX_LENGTH)

    if hidden is not None:
        question.hidden = hidden

    if label is not None:
        question.label = label

    if response_type is not None:
        question.type = response_type

    if question.type.is_precise:
        question.responses = []

        if not year:
            abort(400, "Year must be specified")

        try:
            int(year)
        except Exception:
            abort(400, "Year must be an int")

        if int(year) > YEAR_MAX or int(year) < YEAR_MIN:
            abort(400, f"Year must be between {YEAR_MIN} and {YEAR_MAX}")

        question.year = year
    else:
        question.year = None

    if not question.type.is_precise and (
        true_response_uuid is not None or false_responses_uuid is not None
    ):
        question.responses = []

        responses_filter_uuid_in = []

        if true_response_uuid is not None:
            responses_filter_uuid_in += [true_response_uuid]

        if false_responses_uuid is not None:
            responses_filter_uuid_in += false_responses_uuid

        responses = repo_response.list_(
            filter_uuid_in=[true_response_uuid] + false_responses_uuid
        )

        if true_response_uuid is not None:
            true_response = next(
                (res for res in responses if res.uuid == true_response_uuid), None
            )

            if true_response == None:
                abort(404, "Right response specified does not exist")

        if false_responses_uuid is not None:
            false_responses = [
                res for res in responses if res.uuid in false_responses_uuid
            ]

            if len(false_responses) != len(false_responses_uuid):
                abort(
                    404,
                    f"{len(false_responses_uuid) - len(false_responses)} false responses specified were not found",
                )

        question_response = QuestionResponse(
            question.id, true_response.id, QuestionResponseStatus.CORRECT
        )

        db.session.add(question_response)

        for res in false_responses:
            question_response = QuestionResponse(
                question.id, res.id, QuestionResponseStatus.WRONG
            )
            db.session.add(question_response)

    db.session.add(question)
    db.session.commit()

    return question
