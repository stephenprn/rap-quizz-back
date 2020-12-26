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
