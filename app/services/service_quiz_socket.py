from typing import Tuple
import sched
from datetime import datetime, timedelta

from flask_socketio import join_room, leave_room, close_room, emit, rooms
from flask_jwt_extended import get_jwt_identity

from app.shared.socketio import socketio
from app.shared.annotations import convert_to_json
from app.repositories import QuizQuestionRepository, QuestionRepository, QuizRepository, UserQuizRepository
from app.utils import utils_date
from app.services import service_quiz
from app.classes import QuizRoom, QuizPlayer
from app.models import QuizStatus, UserQuizStatus

QUIZ_ROOM_PREFIX = 'quiz-'

repo_quiz = QuizRepository()
repo_quiz_question = QuizQuestionRepository()
repo_user_quiz = UserQuizRepository()

quizzes = {}


def join_quiz(quiz_uuid: str) -> None:
    room_name = __get_room_name(quiz_uuid)

    if room_name in quizzes and quizzes[room_name].status != QuizStatus.WAITING:
        return

    user, admin = __join_room(quiz_uuid, __get_user())
    __emit_event(room_name, 'user_joined', {
        'user': user,
        'admin': admin
    })


def leave_quiz(quiz_uuid: str) -> None:
    room_name = __get_room_name(quiz_uuid)
    user = __get_user()

    __leave_room(quiz_uuid, user)
    __emit_event(room_name, 'user_leaved', user)

    service_quiz.leave_quiz(quiz_uuid)


def start_quiz(quiz_uuid: str) -> None:
    room_name = __get_room_name(quiz_uuid)
    quiz_room = quizzes[room_name]
    user = __get_user()

    if not quiz_room.is_admin(user['uuid']):
        return

    quiz_questions = repo_quiz_question.get_all_by_quiz_uuid(quiz_uuid)
    quiz_room.add_questions(quiz_questions)

    __emit_event(room_name, 'started',
                 quizzes[room_name].get_question())

    quiz_room.set_status(QuizStatus.ONGOING)
    repo_quiz.set_status_by_uuid(quiz_uuid, QuizStatus.ONGOING)
    __schedule_timer_next_question(quiz_uuid, quiz_room.question_duration)



def answer_response(quiz_uuid: str, question_uuid: str, response_uuid: str) -> None:
    room_name = __get_room_name(quiz_uuid)
    user = __get_user()

    answer_correct = quizzes[room_name].player_answer(
        user['uuid'], question_uuid, response_uuid)

    __emit_event(room_name, 'user_answered', {
                 'user': user, 'answer_correct': answer_correct})

    if quizzes[room_name].all_players_answered():
        quizzes[room_name].cancel_question_scheduler()
        __next_question(quiz_uuid)


def leave_all_quizzes() -> None:
    rooms_names = rooms()

    for room_name in rooms_names:
        if __is_room_quiz(room_name):
            current_identity = get_jwt_identity()
            leave_room(room_name)
            __emit_event(room_name, 'user_leaved', {'username': current_identity['username'],
                                                    'uuid': current_identity['uuid']})


def close_quiz(quiz_uuid: str) -> None:
    room_name = __get_room_name(quiz_uuid)

    close_room(room_name)


def __join_room(quiz_uuid: str, user: dict) -> Tuple[dict, bool]:
    room_name = __get_room_name(quiz_uuid)

    if room_name not in quizzes:
        quiz = repo_quiz.get_one_by_uuid(quiz_uuid)
        quizzes[room_name] = QuizRoom(quiz, user['uuid'])

        admin = True
    else:
        admin = False

    player = QuizPlayer(user['uuid'], user['username'], admin)

    quizzes[room_name].add_player(player)

    join_room(room_name)

    return user, admin


def __leave_room(quiz_uuid: str, user: dict) -> None:
    room_name = __get_room_name(quiz_uuid)

    if room_name not in quizzes:
        return

    quiz_room = quizzes[room_name]

    # if nobody in the room, remove room
    if len(quiz_room.remove_player(user['uuid'])) == 0:
        quizzes.pop(room_name)
    # else set a new admin if needed
    else:
        new_admin = quiz_room.set_admin_if_not_exists()

        if new_admin != None:
            __emit_event(room_name, 'admin_set', {
                'uuid': new_admin.uuid,
                'username': new_admin.username
            })
            repo_user_quiz.set_status(
                quiz_uuid, new_admin.uuid, UserQuizStatus.ADMIN)

    leave_room(room_name)


def __emit_event(room_name: str, event_name: str, event_body: dict = None) -> None:
    emit(event_name, {
        'timestamp': utils_date.get_current_datetime_string(),
        'body': event_body
    }, room=room_name)


def __get_room_name(quiz_uuid: str) -> str:
    return f'{QUIZ_ROOM_PREFIX}{quiz_uuid}'


def __get_user() -> dict:
    current_identity = get_jwt_identity()
    return {'username': current_identity["username"], 'uuid': current_identity['uuid']}


def __is_room_quiz(room_name: str) -> bool:
    return room_name.startswith(QUIZ_ROOM_PREFIX)


def __next_question(quiz_uuid: str) -> None:
    room_name = __get_room_name(quiz_uuid)
    quiz_room = quizzes[room_name]

    quiz_room.increment_index()
    quiz_room.reset_all_players_answer_status()

    question = quiz_room.get_question()

    if question == None:
        __emit_event(room_name, 'finished')

        quiz_room.set_status(QuizStatus.FINISHED)

        repo_quiz.finish_one(quiz_uuid, quiz_room)
        return

    __emit_event(room_name, 'question', question)
    __schedule_timer_next_question(quiz_uuid, quiz_room.question_duration)


# WARNING: This has to be run at the end of the call because blocking
def __schedule_timer_next_question(quiz_uuid: str, question_duration: int):
    room_name = __get_room_name(quiz_uuid)
    scheduler = sched.scheduler()

    event = scheduler.enter(question_duration, 1,
                            __next_question, (quiz_uuid,))
    quizzes[room_name].set_question_scheduler(scheduler, event)
    scheduler.run()
