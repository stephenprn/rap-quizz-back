from flask import json
from werkzeug import exceptions

from app.models import User, UserRole, ResponseType
from app.shared.db import db
from app.services import service_response, service_question, service_auth

PASSWORD_TEST = "password"


def init_test_users():
    print("INIT TEST USERS")

    for username in ["test", "test1", "test2"]:
        try:
            service_auth.register(username + "@test.com", username, PASSWORD_TEST)
        except exceptions.Conflict:
            pass


def init_test_questions():
    print("INIT TEST QUESTIONS")

    for artist, question in [
        ("Orelsan", "Qui a écrit perdu d'avance ?"),
        ("Nekfeu", "Quel rappeur se prénomme Ken Samaras ?"),
        ("Vald", "Quel rappeur est l'auteur des albums NQNT ?"),
        ("Laylow", "Qui a sorti Trinity en 2020 ?"),
        ("Damso", 'Qui est l\'auteur du single "Bruxelles Vie" ?'),
        ("Népal", "Qui est l'auteur du chef d'oeuvre \"Adios Bahamas\" ?"),
    ]:
        try:
            response = service_response.add(artist, ResponseType.ARTIST)
            service_question.add(question, response.uuid)
        except exceptions.Conflict:
            pass
