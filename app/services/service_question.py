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

from app.utils.utils_query import FilterText
from app.utils.utils_string import check_length

repo_question = QuestionRepository()
repo_response = ResponseRepository()

RESPONSES_LIST_SEARCH_TXT_NBR_RESULTS = 5

LABEL_MIN_LENGTH = 8
LABEL_MAX_LENGTH = 100
EXPLAINATION_MAX_LENGTH = 500

YEAR_MIN = 1900
YEAR_MAX = 2100

QUIZ_RANKING_NBR_RESPONSES_MIN = 3
QUIZ_RANKING_NBR_RESPONSES_MAX = 10


def add(
    label: str,
    response_type: ResponseType,
    ranking: bool,
    explaination: Optional[str] = None,
    true_response_uuid: Optional[str] = None,
    false_responses_uuid: Optional[List[str]] = None,
    ranked_responses_uuid: Optional[List[str]] = None,
    year: str = None,
) -> Question:
    check_length(
        label,
        "Label",
        min_length=LABEL_MIN_LENGTH,
        max_length=LABEL_MAX_LENGTH)
    check_length(
        explaination,
        "explaination",
        max_length=EXPLAINATION_MAX_LENGTH)

    if response_type.is_regular and not ranking and not true_response_uuid:
        abort(400, "True response must be specified through true_response_uuid")

    if (
        response_type.is_regular
        and not ranking
        and true_response_uuid in false_responses_uuid
    ):
        abort(400, "True response cannot be in false responses")

    if response_type.is_regular and ranking and not ranked_responses_uuid:
        abort(400, "Ranked responses must be specified through ranked_responses_uuid")

    if (
        response_type.is_regular
        and not ranking
        and len(false_responses_uuid) + 1 > QUIZ_DEFAULT_NBR_RESPONSES
    ):
        abort(
            400,
            f"A question can have a maximum of {QUIZ_DEFAULT_NBR_RESPONSES} responses",
        )

    if (
        response_type.is_regular
        and ranking
        and (
            len(ranked_responses_uuid) > QUIZ_RANKING_NBR_RESPONSES_MAX
            or len(ranked_responses_uuid) < QUIZ_RANKING_NBR_RESPONSES_MIN
        )
    ):
        abort(
            400,
            f"A ranked question must have between {QUIZ_RANKING_NBR_RESPONSES_MIN} and {QUIZ_RANKING_NBR_RESPONSES_MAX} responses",
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

    if repo_question.get(
        filter_label=FilterText(
            label=label,
            ignore_case=True)):
        abort(409, "This question already exists")

    if response_type.is_regular:
        if ranking:
            responses_unordered = repo_response.list_(
                filter_uuid_in=ranked_responses_uuid
            )
        else:
            responses = repo_response.list_(
                filter_uuid_in=[true_response_uuid] + false_responses_uuid
            )

        if any([r.type != response_type for r in responses]):
            abort(
                400,
                f"Responses specified must be the same type as the question type: {response_type}",
            )

        if not ranking:
            true_response = next(
                (res for res in responses if res.uuid == true_response_uuid), None)
            false_responses = [
                res for res in responses if res.uuid in false_responses_uuid
            ]

            if true_response is None:
                abort(404, "Right response specified does not exist")

            if len(false_responses) != len(false_responses_uuid):
                abort(
                    404,
                    f"{len(false_responses_uuid) - len(false_responses)} false responses specified were not found",
                )
        elif ranking and len(ranked_responses_uuid) != len(responses_unordered):
            abort(
                404,
                f"{len(ranked_responses_uuid) - len(responses_unordered)} ranked responses specified were not found",
            )

    question = Question(label)
    question.type = response_type
    question.sub_type = (
        QuestionSubType.UNKNOWN if not ranking else QuestionSubType.RANKING
    )

    if explaination:
        question.explaination = explaination

    if response_type.is_precise:
        question.response_precise = year

    db.session.add(question)
    db.session.commit()

    if response_type.is_precise:
        return question

    if not ranking:
        question_response = QuestionResponse(
            question.id, true_response.id, QuestionResponseStatus.CORRECT
        )

        db.session.add(question_response)

        for res in false_responses:
            question_response = QuestionResponse(
                question.id, res.id, QuestionResponseStatus.WRONG
            )
            db.session.add(question_response)
    else:
        for i, uuid in enumerate(ranked_responses_uuid):
            res = next(r for r in responses_unordered if r.uuid == uuid)
            question_response = QuestionResponse(question.id, res.id, index=i)
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
    ranking: bool = None,
    explaination: Optional[str] = None,
    response_type: Optional[ResponseType] = None,
    sub_type: Optional[QuestionSubType] = None,
    true_response_uuid: Optional[str] = None,
    false_responses_uuid: Optional[List[str]] = None,
    ranked_responses_uuid: List[str] = None,
    year: str = None,
):
    question = repo_question.get(
        filter_uuid_in=[question_uuid],
        load_full_response=True,
    )

    if question is None:
        abort(404, "Question not found")

    if label is not None:
        check_length(
            label,
            "Label",
            min_length=LABEL_MIN_LENGTH,
            max_length=LABEL_MAX_LENGTH)

    if hidden is not None:
        question.hidden = hidden

    if explaination is not None:
        question.explaination = explaination if explaination else None

    if label is not None:
        question.label = label

    if response_type is not None:
        question.type = response_type

    if sub_type is not None:
        question.sub_type = sub_type

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

    if (question.type.is_regular and not ranking and (
            true_response_uuid is not None or false_responses_uuid is not None)):
        question.responses = []
        responses_filter_uuid_in = []

        if true_response_uuid is not None:
            responses_filter_uuid_in += [true_response_uuid]

        if false_responses_uuid is not None:
            responses_filter_uuid_in += false_responses_uuid

        responses = repo_response.list_(
            filter_uuid_in=responses_filter_uuid_in)

        if true_response_uuid is not None:
            true_response = next(
                (res for res in responses if res.uuid == true_response_uuid), None)

            if true_response is None:
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
    elif question.type.is_regular and ranking and ranked_responses_uuid is not None:
        question.responses = []

        responses_unordered = repo_response.list_(
            filter_uuid_in=ranked_responses_uuid)

        if len(responses_unordered) != len(ranked_responses_uuid):
            abort(
                404,
                f"{len(ranked_responses_uuid) - len(responses_unordered)} ranked responses specified were not found",
            )

        for i, uuid in enumerate(ranked_responses_uuid):
            res = next(r for r in responses_unordered if r.uuid == uuid)
            question_response = QuestionResponse(question.id, res.id, index=i)
            db.session.add(question_response)

    db.session.add(question)
    db.session.commit()

    return question
