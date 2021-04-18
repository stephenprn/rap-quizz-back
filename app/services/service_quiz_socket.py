from typing import Tuple
import sched
from datetime import datetime, timedelta

from flask_socketio import join_room, leave_room, close_room, emit, rooms
from flask_jwt_extended import get_jwt_identity

from app.shared.db import db

from app.repositories import (
    QuizQuestionRepository,
    QuizRepository,
    UserQuizRepository,
)
from app.utils import utils_date
from app.services import service_quiz
from app.classes import QuizRoom, QuizPlayer
from app.models import QuizStatus, UserQuizStatus

QUIZ_ROOM_PREFIX = "quiz-"
START_COUNTDOWN_SEC = 3

repo_quiz = QuizRepository()
repo_quiz_question = QuizQuestionRepository()
repo_user_quiz = UserQuizRepository()

quizzes = {}


def join_quiz(quiz_uuid: str) -> None:
    room_name = __get_room_name(quiz_uuid)

    if room_name in quizzes and quizzes[room_name].status != QuizStatus.WAITING:
        return

    user, admin = __join_room(quiz_uuid, __get_user())
    __emit_event(room_name, "user_joined", {"user": user, "admin": admin})


def leave_quiz(quiz_uuid: str) -> None:
    room_name = __get_room_name(quiz_uuid)
    quiz_room = quizzes[room_name]
    user = __get_user()

    __leave_room(quiz_uuid, user)
    __emit_event(room_name, "user_leaved", user)

    service_quiz.leave_quiz(quiz_uuid, quiz_room.status)


def start_quiz(quiz_uuid: str) -> None:
    room_name = __get_room_name(quiz_uuid)
    quiz_room = quizzes[room_name]
    user = __get_user()

    if not quiz_room.is_admin(user["uuid"]):
        return

    quiz_questions = repo_quiz_question.list_(
        filter_quiz_uuid_in=[quiz_uuid], load_only_response_label=True
    )
    quiz_room.add_questions(quiz_questions)

    __emit_event(room_name, "started", quizzes[room_name].get_question())

    quiz_room.set_status(QuizStatus.ONGOING)
    __set_quiz_status(quiz_uuid, QuizStatus.ONGOING)
    quiz_room.set_last_question_date(
        datetime.now() + timedelta(seconds=START_COUNTDOWN_SEC)
    )
    __schedule_timer_next_question(
        quiz_uuid, question_duration=quiz_room.question_duration, first_schedule=True
    )


def answer_response(quiz_uuid: str, question_uuid: str, response_uuid: str) -> None:
    room_name = __get_room_name(quiz_uuid)
    quizzes[room_name]
    user = __get_user()

    answer_correct, score, score_total = quizzes[room_name].player_answer(
        user["uuid"], question_uuid, response_uuid
    )

    __emit_event(
        room_name,
        "user_answered",
        {
            "user": user,
            "answer_correct": answer_correct,
            "score": score,
            "score_total": score_total,
        },
    )

    if quizzes[room_name].all_players_answered():
        quizzes[room_name].cancel_question_scheduler()
        __next_question(quiz_uuid)


def leave_all_quizzes() -> None:
    rooms_names = rooms()

    for room_name in rooms_names:
        if __is_room_quiz(room_name):
            current_identity = get_jwt_identity()
            leave_room(room_name)
            __emit_event(
                room_name,
                "user_leaved",
                {
                    "username": current_identity["username"],
                    "uuid": current_identity["uuid"],
                },
            )


def close_quiz(quiz_uuid: str) -> None:
    room_name = __get_room_name(quiz_uuid)

    close_room(room_name)


def __join_room(quiz_uuid: str, user: dict) -> Tuple[dict, bool]:
    room_name = __get_room_name(quiz_uuid)

    if room_name not in quizzes:
        quiz = repo_quiz.get(filter_uuid_in=[quiz_uuid])
        quizzes[room_name] = QuizRoom(quiz, user["uuid"])

        admin = True
    else:
        admin = False

    player = QuizPlayer(user["uuid"], user["username"], admin)

    quizzes[room_name].add_player(player)

    join_room(room_name)

    return user, admin


def __leave_room(quiz_uuid: str, user: dict) -> None:
    room_name = __get_room_name(quiz_uuid)

    if room_name not in quizzes:
        return

    quiz_room = quizzes[room_name]
    quiz_room.remove_player(user["uuid"])

    # if nobody in the room, remove room
    if len(quiz_room.players) == 0:
        quizzes.pop(room_name)
    # else set a new admin if needed
    else:
        new_admin = quiz_room.set_admin_if_not_exists()

        if new_admin != None:
            __emit_event(
                room_name,
                "admin_set",
                {"uuid": new_admin.uuid, "username": new_admin.username},
            )
            user_quiz = repo_user_quiz.get(
                filter_quiz_uuid_in=[quiz_uuid], filter_user_uuid_in=[user_uuid]
            )
            user_quiz.status = UserQuizStatus.ADMIN
            db.session.commit()

    leave_room(room_name)


def __emit_event(room_name: str, event_name: str, event_body: dict = None) -> None:
    emit(
        event_name,
        {"timestamp": utils_date.get_current_datetime_string(), "body": event_body},
        room=room_name,
    )


def __get_room_name(quiz_uuid: str) -> str:
    return f"{QUIZ_ROOM_PREFIX}{quiz_uuid}"


def __get_user() -> dict:
    current_identity = get_jwt_identity()
    return {
        "username": current_identity["username"],
        "uuid": current_identity["uuid"],
        "color": current_identity["color"],
    }


def __is_room_quiz(room_name: str) -> bool:
    return room_name.startswith(QUIZ_ROOM_PREFIX)


def __next_question(quiz_uuid: str) -> None:
    room_name = __get_room_name(quiz_uuid)
    quiz_room = quizzes[room_name]

    quiz_room.increment_index()
    quiz_room.reset_all_players_answer_status()

    question = quiz_room.get_question()

    if question == None:
        __emit_event(room_name, "finished")

        quiz_room.set_status(QuizStatus.FINISHED)
        __finish_quiz(quiz_uuid, quiz_room)
        return

    quiz_room.set_last_question_date()
    __emit_event(room_name, "question", question)
    __schedule_timer_next_question(quiz_uuid, quiz_room.question_duration)


def __finish_quiz(uuid: str, quiz_room: QuizRoom):
    quiz = repo_quiz.get(filter_uuid_id=[uuid], load_only_users=True)
    quiz.status = QuizStatus.FINISHED

    for user_quiz in quiz.users:
        player = quiz_room.get_player(user_quiz.user.uuid)
        user_quiz.score = player.score
        user_quiz.user_leaved_quiz_status = QuizStatus.FINISHED

    db.session.commit()


def __set_quiz_status(uuid: str, status: QuizStatus) -> None:
    quiz = repo_quiz.get(filter_uuid_in=[uuid])
    quiz.status = status
    db.session.commit()


# WARNING: This has to be run at the end of the call because blocking


def __schedule_timer_next_question(
    quiz_uuid: str, question_duration: int = None, first_schedule: bool = False
):
    if question_duration == 0:
        return

    room_name = __get_room_name(quiz_uuid)
    scheduler = sched.scheduler()

    if first_schedule:
        question_duration += START_COUNTDOWN_SEC

    event = scheduler.enter(question_duration, 1, __next_question, (quiz_uuid,))
    quizzes[room_name].set_question_scheduler(scheduler, event)
    scheduler.run()
