from flask import abort
from sqlalchemy.orm import load_only, joinedload
from sqlalchemy import desc
from random import shuffle
from typing import List, Tuple

import app.models

from app.utils.utils_string import normalize_string, check_length, generate_random_string
from app.utils.utils_date import get_current_date_string

from app.repositories import QuestionRepository
from app.repositories import QuestionResponseRepository
from app.repositories import QuizRepository
from app.repositories import UserQuizRepository
from app.repositories import QuizQuestionRepository

from app.services import service_quiz_socket, service_auth

from app.shared.db import db
from app.shared.annotations import to_json, convert_to_dict, convert_to_json

from app.models import (
    UserQuiz,
    QuizQuestion,
    UserQuizStatus,
    QuestionResponse,
    QuizQuestionResponse,
    QuestionResponseStatus,
    Quiz, QuizStatus,
    Question, Response
)

repo_quiz = QuizRepository()
repo_question = QuestionRepository()
repo_question_response = QuestionResponseRepository()
repo_user_quiz = UserQuizRepository()
repo_quiz_question = QuizQuestionRepository()

URL_SEPARATOR = "-"

NAME_MIN_LENGTH = 5
NAME_MAX_LENGTH = 100

QUIZ_QUESTION_DEFAULT_DURATION_SEC = 30
QUIZ_DEFAULT_NBR_QUESTIONS = 10
QUIZ_DEFAULT_NBR_ADDITIONAL_RESPONSES = 3
QUIZ_URL_RANDOM_STR_LENGTH = 6


def get_quizzes_list(nbr_results: int, page_nbr: int) -> dict:
    res = (
        db.session.query(Quiz)
        .options(load_only("name", "url", "creation_date"))
        .order_by(desc(Quiz.creation_date))
        .paginate(page=page_nbr, per_page=nbr_results, error_out=False)
    )

    return {"total": res.total, "data": res.items}


def generate_quiz(name: str = None, nbr_questions: int = QUIZ_DEFAULT_NBR_QUESTIONS, question_duration: int = QUIZ_QUESTION_DEFAULT_DURATION_SEC) -> str:
    if name == None:
        name = get_current_date_string()

    quiz = Quiz(name, __generate_unique_url(name),
                nbr_questions, question_duration)

    db.session.add(quiz)
    db.session.commit()

    current_identity = service_auth.get_current_identity()
    user_quiz = UserQuiz(current_identity.id, quiz.id, UserQuizStatus.ADMIN)

    db.session.add(user_quiz)
    db.session.commit()

    __generate_questions(quiz, nbr_questions)

    quiz_dict = convert_to_dict(quiz)
    quiz_dict["questions"] = []

    return convert_to_json(quiz_dict)


def join_quiz(quiz_url: str) -> Quiz:
    quiz = repo_quiz.get_one_by_url(quiz_url, with_users=True)

    if quiz == None:
        abort(404, 'Quiz not found')
    elif quiz.status == QuizStatus.ONGOING:
        abort(400, 'Quiz already started')
    elif quiz.status == QuizStatus.FINISHED:
        abort(400, 'Quiz already finished')

    current_identity = service_auth.get_current_identity()

    if repo_user_quiz.get_by_quiz_id_user_id(quiz.id, current_identity.id) is not None:
        abort(409, 'User is already in this quiz')

    user_quiz = UserQuiz(
        current_identity.id,
        quiz.id,
        UserQuizStatus.PLAYER
    )

    db.session.add(user_quiz)
    db.session.commit()

    return quiz


def leave_quiz(quiz_uuid: str) -> None:
    current_identity = service_auth.get_current_identity()
    user_quiz = repo_user_quiz.get_by_quiz_uuid_user_id(
        quiz_uuid, current_identity.id)

    if user_quiz == None:
        abort(404, 'User not in this quiz or quiz does not exists')
        return

    db.session.delete(user_quiz)
    db.session.commit()


def __generate_questions(
    quiz: Quiz, nbr_questions: int, exclude_questions_ids: List[id] = None
) -> List[Question]:
    questions = repo_question.get_random_for_quiz(
        nbr_questions, exclude_questions_ids=exclude_questions_ids
    )

    for index, question in enumerate(questions):
        false_questions_responses = __generate_false_responses(question)
        quiz_question = QuizQuestion(quiz.id, question.id, index)

        db.session.add(quiz_question)
        db.session.commit()

        for question_response in false_questions_responses:
            quiz_question_response = QuizQuestionResponse(
                quiz_question.id, question_response.response_id
            )

            db.session.add(quiz_question_response)
            db.session.commit()

    db.session.commit()

    return questions


def generate_question_dict(
    question: Question, false_questions_responses: List[QuestionResponse]
) -> Tuple[dict, Response]:
    correct_response = next(
        response for response in question.responses if response.status == QuestionResponseStatus.CORRECT)
    question_dict = convert_to_dict(question)

    for response_dict in question_dict["responses"]:
        response_dict.pop('status')

    question_dict["responses"].extend(
        convert_to_dict(false_questions_responses))

    shuffle(question_dict["responses"])

    return question_dict, correct_response


def __generate_false_responses(question: Question) -> QuestionResponse:
    return repo_question_response.get_random_for_quiz(
        question.type,
        QUIZ_DEFAULT_NBR_ADDITIONAL_RESPONSES,
        [question.responses[0].response.id],
    )


def __generate_unique_url(name: str) -> str:
    url_base = normalize_string(name, replace_spaces=URL_SEPARATOR)

    while True:
        url_sufix = generate_random_string(QUIZ_URL_RANDOM_STR_LENGTH)
        url = url_base + URL_SEPARATOR + url_sufix

        if db.session.query(Quiz.id).filter_by(url=url).scalar() is None:
            break

    return url
