from flask import abort

from app.shared.db import db
from app.shared.annotations import to_json

from app.repositories import QuestionRepository
from app.repositories import ResponseRepository
from app.models import Question
from app.models import QuestionResponse, QuestionResponseStatus

from app.utils.utils_string import normalize_string, check_length

repo_question = QuestionRepository()
repo_response = ResponseRepository()

RESPONSES_LIST_SEARCH_TXT_NBR_RESULTS = 5

LABEL_MIN_LENGTH = 8
LABEL_MAX_LENGTH = 100


def add(label: str, response_uuid: str) -> Question:
    check_length(label, "Label", LABEL_MIN_LENGTH, LABEL_MAX_LENGTH)

    # label_normalized = normalize_string(label)

    if repo_question.get(label) != None:
        abort(409, "This question already exists")

    response = repo_response.get_by_uuid(response_uuid)

    if response == None:
        abort(404, "Response specified does not exist")

    question = Question(label)
    question.type = response.type

    db.session.add(question)
    db.session.commit()

    question_response = QuestionResponse(
        question.id, response.id, QuestionResponseStatus.CORRECT
    )

    db.session.add(question_response)
    db.session.commit()

    return question


def list_(nbr_results: int, page_nbr: int, hidden: bool = None):
    return repo_question.list_(nbr_results, page_nbr, hidden=hidden)

def hide(question_uuid: str, hidden: bool):
    question = repo_question.get(uuid=question_uuid)

    question.hidden = hidden

    db.session.add(question)
    db.session.commit()
