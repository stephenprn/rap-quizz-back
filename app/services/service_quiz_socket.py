from flask_socketio import join_room, leave_room, emit
from flask_jwt import current_identity

from app.utils import utils_date


def join_quiz(quiz_uuid: str):
    room_name = __get_room_name(quiz_uuid)

    join_room(room_name)
    __emit_event(room_name, 'user_joined', {'username': current_identity.username,
                                            'uuid': current_identity.uuid})


def leave_quiz(quiz_uuid: str):
    room_name = __get_room_name(quiz_uuid)

    leave_room(room_name)
    __emit_event(room_name, 'user_leaved', {'username': current_identity.username,
                                            'uuid': current_identity.uuid})


def __emit_event(room_name: str, event_name: str, event_body: dict):
    emit(event_name, {
        'timestamp': utils_date.get_current_datetime_string(),
        'body': event_body
    }, room=room_name)


def __get_room_name(quiz_uuid: str):
    return f'quiz-{quiz_uuid}'
