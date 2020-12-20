from flask import abort

from app.shared.db import db
from app.shared.annotations import to_json

from app.repositories import QuestionRepository
from app.repositories import ResponseRepository
from app.models import Question
from app.models import QuestionResponse, QuestionResponseStatus

from app.utils.utils_string import normalize_string, check_length

repo = QuestionRepository()
repo_response = ResponseRepository()

RESPONSES_LIST_SEARCH_TXT_NBR_RESULTS = 5

LABEL_MIN_LENGTH = 8
LABEL_MAX_LENGTH = 100


@to_json()
def add(label: str, response_uuid: str):
    check_length(label, "Label", LABEL_MIN_LENGTH, LABEL_MAX_LENGTH)

    # label_normalized = normalize_string(label)

    if repo.get(label) != None:
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
