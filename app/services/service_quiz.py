from flask import abort
from sqlalchemy.orm import load_only
from sqlalchemy import desc
from random import shuffle
from typing import List


from app.utils.utils_string import (
    normalize_string,
    generate_random_string,
)
from app.utils.utils_date import get_current_date_string

from app.repositories import QuestionRepository
from app.repositories import QuestionResponseRepository
from app.repositories import QuizRepository
from app.repositories import UserQuizRepository
from app.repositories import ResponseRepository

from app.services import service_auth

from app.shared.db import db
from app.shared.annotations import convert_to_dict, convert_to_json

from app.models import (
    UserQuiz,
    QuizQuestion,
    UserQuizStatus,
    QuestionResponse,
    QuizQuestionResponse,
    QuestionResponseStatus,
    Quiz,
    QuizStatus,
    Question,
    Response,
)

repo_quiz = QuizRepository()
repo_question = QuestionRepository()
repo_question_response = QuestionResponseRepository()
repo_user_quiz = UserQuizRepository()
repo_response = ResponseRepository()

URL_SEPARATOR = "-"

NAME_MIN_LENGTH = 5
NAME_MAX_LENGTH = 100

QUIZ_QUESTION_DEFAULT_DURATION_SEC = 30
QUIZ_DEFAULT_NBR_QUESTIONS = 10
QUIZ_DEFAULT_NBR_RESPONSES = 4
QUIZ_URL_RANDOM_STR_LENGTH = 6
QUIZ_MAX_PLAYERS = 10


def get_quizzes_list(nbr_results: int, page_nbr: int) -> dict:
    res = (
        db.session.query(Quiz)
        .options(load_only("name", "url", "creation_date"))
        .order_by(desc(Quiz.creation_date))
        .paginate(page=page_nbr, per_page=nbr_results, error_out=False)
    )

    return {"total": res.total, "data": res.items}


def generate_quiz(
    name: str = None,
    nbr_questions: int = QUIZ_DEFAULT_NBR_QUESTIONS,
    question_duration: int = QUIZ_QUESTION_DEFAULT_DURATION_SEC,
) -> str:
    if name == None:
        name = get_current_date_string()

    quiz = Quiz(name, __generate_unique_url(name), nbr_questions, question_duration)

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
    quiz = repo_quiz.get(filter_url_in=[quiz_url], load_only_users=True)

    if quiz == None:
        abort(404, "Quiz not found")
    elif quiz.status == QuizStatus.ONGOING:
        abort(400, "Quiz already started")
    elif quiz.status == QuizStatus.FINISHED:
        abort(400, "Quiz already finished")

    current_identity = service_auth.get_current_identity()

    user_quiz = repo_user_quiz.get(
        filter_quiz_id_in=[quiz.id],
        filter_user_id_in=[current_identity.id],
        load_only_status_username=True,
    )

    if user_quiz is not None and user_quiz.user_leaved_quiz_status is None:
        abort(409, "User is already in this quiz")

    if (
        repo_user_quiz.count(
            filter_quiz_id_in=[quiz.id], filter_null_user_leaved_quiz_status=True
        )
        >= QUIZ_MAX_PLAYERS
    ):
        abort(409, "Too many players in this quiz")

    if user_quiz is None:
        user_quiz = UserQuiz(current_identity.id, quiz.id, UserQuizStatus.PLAYER)

        db.session.add(user_quiz)
        db.session.commit()
    else:
        user_quiz.user_leaved_quiz_status = None

    # return all players except me
    quiz_dict = convert_to_dict(quiz)
    quiz_dict["users"] = [
        quiz_user
        for quiz_user in quiz_dict["users"]
        if quiz_user["user"]["uuid"] != current_identity.uuid
    ]

    return convert_to_json(quiz_dict)


def leave_quiz(quiz_uuid: str, quiz_status: QuizStatus) -> None:
    current_identity = service_auth.get_current_identity()
    user_quiz = repo_user_quiz.get(
        filter_quiz_uuid_in=[quiz_uuid], filter_user_id_in=[current_identity.id]
    )

    if user_quiz is None:
        abort(404, "User not in this quiz or quiz does not exists")
        return

    if user_quiz.user_leaved_quiz_status is not None:
        abort(409, "User already leaved this")
        return

    user_quiz.status = UserQuizStatus.PLAYER
    user_quiz.user_leaved_quiz_status = quiz_status
    db.session.commit()


def __generate_questions(
    quiz: Quiz, nbr_questions: int, exclude_questions_ids: List[id] = None
) -> List[Question]:
    questions = repo_question.list_(
        nbr_results=nbr_questions,
        order_random=True,
        load_only_response_label=True,
        filter_question_id_not_in=exclude_questions_ids,
        filter_hidden=False,
        filter_responses_hidden=False,
    )

    for index, question in enumerate(questions):
        false_responses = []

        if (
            not question.type.is_precise
            and len(question.responses) < QUIZ_DEFAULT_NBR_RESPONSES
        ):
            false_responses = __generate_false_responses(question)

        quiz_question = QuizQuestion(quiz.id, question.id, index)

        db.session.add(quiz_question)
        db.session.commit()

        for response in false_responses:
            quiz_question_response = QuizQuestionResponse(quiz_question.id, response.id)

            db.session.add(quiz_question_response)
            db.session.commit()

    db.session.commit()

    return questions


def generate_question_dict(
    question: Question, false_questions_responses: List[QuestionResponse]
) -> dict:
    if not question.type.is_precise:
        correct_response = next(
            response
            for response in question.responses
            if response.status == QuestionResponseStatus.CORRECT
        ).response.uuid
    else:
        correct_response = question.response_precise

    question_dict = convert_to_dict(question)
    question_dict.pop("response_precise", None)

    for response_dict in question_dict["responses"]:
        response_dict.pop("status")

    question_dict["responses"].extend(convert_to_dict(false_questions_responses))

    shuffle(question_dict["responses"])

    return {
        "question_dict": question_dict,
        "correct_response": correct_response,
    }


def __generate_false_responses(question: Question) -> Response:
    return repo_response.list_(
        filter_id_not_in=[qr.response.id for qr in question.responses],
        filter_type_in=[question.type],
        filter_hidden=False,
        order_random=True,
        nbr_results=QUIZ_DEFAULT_NBR_RESPONSES - len(question.responses),
        page_nbr=0,
    )


def __generate_unique_url(name: str) -> str:
    url_base = normalize_string(name, replace_spaces=URL_SEPARATOR)

    while True:
        url_sufix = generate_random_string(QUIZ_URL_RANDOM_STR_LENGTH)
        url = url_base + URL_SEPARATOR + url_sufix

        if db.session.query(Quiz.id).filter_by(url=url).scalar() is None:
            break

    return url
