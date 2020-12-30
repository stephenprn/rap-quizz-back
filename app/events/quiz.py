from flask_jwt import jwt_required

from app.shared.socketio import socketio

from app.services import service_quiz_socket

# https://github.com/miguelgrinberg/Flask-SocketIO-Chat/tree/master/app/main
# https://flask-socketio.readthedocs.io/en/latest/


@socketio.on('join', namespace="/quiz")
@jwt_required()
def join_quiz(quiz_uuid: str):
    service_quiz_socket.join_quiz(quiz_uuid)


@socketio.on('close', namespace="/quiz")
@jwt_required()
def leave_quiz(quiz_uuid: str):
    service_quiz_socket.leave_quiz(quiz_uuid)


@socketio.on('start', namespace="/quiz")
@jwt_required()
def start_quiz(quiz_uuid: str):
    service_quiz_socket.start_quiz(quiz_uuid)


@socketio.on('answer_response', namespace="/quiz")
@jwt_required()
def answer_response(data: dict):
    quiz_uuid = data.get('quiz_uuid')
    question_uuid = data.get('question_uuid')
    response_uuid = data.get('response_uuid')

    service_quiz_socket.answer_response(quiz_uuid, question_uuid, response_uuid)