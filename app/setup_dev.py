from werkzeug import exceptions

from app.repositories import ArtistRepository
from app.models import ResponseType
from app.services import (
    service_response,
    service_question,
    service_auth,
    service_crawler,
    service_question_generator,
)

PASSWORD_TEST = "password"

repo_artist = ArtistRepository()


def init_test_users():
    print("INIT TEST USERS")

    for username in ["test", "test1", "test2"]:
        try:
            service_auth.register(username + "@test.com", username, PASSWORD_TEST)
        except exceptions.Conflict:
            pass


def init_test_simple_questions():
    print("INIT TEST SIMPLE QUESTIONS")

    for artist, question in [
        ("Orelsan", "Qui a écrit perdu d'avance ?"),
        ("Nekfeu", "Quel rappeur se prénomme Ken Samaras ?"),
        ("Vald", "Quel rappeur est l'auteur des albums NQNT ?"),
        ("Laylow", "Qui a sorti Trinity en 2020 ?"),
        ("Damso", 'Qui est l\'auteur du single "Bruxelles Vie" ?'),
        ("Népal", "Qui est l'auteur du chef d'oeuvre \"Adios Bahamas\" ?"),
    ]:
        try:
            response = service_response.add_simple(artist, ResponseType.ARTIST)
            service_question.add(question, response.uuid)
        except exceptions.Conflict:
            pass


def init_test_questions():
    print("INIT TEST QUESTIONS")

    vald_genius_id = 19217
    artist = repo_artist.get(filter_genius_id_in=[vald_genius_id])

    if not artist:
        artist = service_crawler.crawl_artist_full(vald_genius_id)

    service_question_generator.generate_questions_artist(artist)
