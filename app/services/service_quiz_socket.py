from flask_socketio import join_room, leave_room, close_room, emit, rooms
from flask_jwt import current_identity

from app.shared.annotations import convert_to_json
from app.repositories import QuizQuestionRepository, QuestionRepository
from app.utils import utils_date
from app.services import service_quiz
from app.classes import QuizRoom, QuizPlayer

QUIZ_ROOM_PREFIX = 'quiz-'

repo_question = QuestionRepository()
repo_quiz_question = QuizQuestionRepository()

rooms = {}


def join_quiz(quiz_uuid: str):
    room_name = __get_room_name(quiz_uuid)
    user = __get_user()

    __join_room(room_name, user)
    __emit_event(room_name, 'user_joined', user)


def leave_quiz(quiz_uuid: str):
    room_name = __get_room_name(quiz_uuid)
    user = __get_user()

    __leave_room(room_name, user)
    __emit_event(room_name, 'user_leaved', user)


def start_quiz(quiz_uuid: str):
    room_name = __get_room_name(quiz_uuid)

    quiz_questions = repo_quiz_question.get_all_by_quiz_uuid(quiz_uuid)
    rooms[room_name].add_questions(quiz_questions)

    __emit_event(room_name, 'started', rooms[room_name].get_question())


def answer_response(quiz_uuid: str, question_uuid: str, response_uuid: str):
    room_name = __get_room_name(quiz_uuid)
    user = __get_user()

    answer_correct = rooms[room_name].player_answer(
        user['uuid'], question_uuid, response_uuid)

    __emit_event(room_name, 'user_answered', {
                 'user': user, 'answer_correct': answer_correct})

    if rooms[room_name].all_players_answered():
        rooms[room_name].reset_all_players_answer_status()
        __next_question(room_name)


def leave_all_quizzes():
    rooms_names = rooms()

    for room_name in rooms:
        if __is_room_quiz(room_name):
            leave_room(room_name)
            __emit_event(room_name, 'user_leaved', {'username': current_identity.username,
                                                    'uuid': current_identity.uuid})


def close_quiz(quiz_uuid: str):
    room_name = __get_room_name(quiz_uuid)

    close_room(room_name)


def __join_room(room_name: str, user: dict):
    if room_name not in rooms:
        rooms[room_name] = QuizRoom(room_name)

    rooms[room_name].add_player(QuizPlayer(user['uuid'], user['username']))

    join_room(room_name)


def __leave_room(room_name: str, user: dict):
    if room_name not in rooms:
        return

    # if nobody in the room, remove room
    if len(rooms[room_name].remove_player(user['uuid'])) == 0:
        rooms.pop(room_name)

    leave_room(room_name)


def __emit_event(room_name: str, event_name: str, event_body: dict = None):
    emit(event_name, {
        'timestamp': utils_date.get_current_datetime_string(),
        'body': event_body
    }, room=room_name)


def __get_room_name(quiz_uuid: str):
    return f'{QUIZ_ROOM_PREFIX}{quiz_uuid}'


def __get_user():
    return {'username': current_identity.username, 'uuid': current_identity.uuid}


def __is_room_quiz(room_name: str):
    return room_name.startswith(QUIZ_ROOM_PREFIX)


def __next_question(room_name: str):
    rooms[room_name].increment_index()

    question = rooms[room_name].get_question()

    if question == None:
        __emit_event(room_name, 'finished')
        return

    __emit_event(room_name, 'question', question)

