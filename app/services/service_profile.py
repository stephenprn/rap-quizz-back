from flask import abort
from typing import List
from flask_jwt_extended import get_jwt_identity

from app.shared.db import db
from app.shared.annotations import to_json

from app.repositories import UserQuizRepository
from app.models import Question, UserQuiz
from app.models import QuestionResponse, QuestionResponseStatus

from app.utils.utils_string import normalize_string, check_length

repo_user_quiz = UserQuizRepository()


def get_history(nbr_results: int, page_nbr: int) -> List[UserQuiz]:
    current_identity = get_jwt_identity()
    return repo_user_quiz.get_by_user_id(current_identity["id"], nbr_results, page_nbr)
