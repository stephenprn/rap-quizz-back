from flask_socketio import SocketIO
from flask import json

socketio = SocketIO(logger=True, engineio_logger=True, json=json)
