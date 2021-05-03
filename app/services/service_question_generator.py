from typing import List

from app.shared.db import db
from app.models import (
    Artist,
    QuestionSubType,
    ResponseType,
    Question,
    QuestionResponse,
    QuestionResponseStatus,
)
from app.repositories import SongRepository, QuestionRepository

repo_song = SongRepository()
repo_question = QuestionRepository()


def generate_questions_artist(artist: Artist, sub_types: List[QuestionSubType] = None):
    if sub_types is None:
        sub_types = QuestionSubType

    for sub_type in sub_types:
        if RESPONSE_SUB_TYPE_MAPPING.get(sub_type):
            RESPONSE_SUB_TYPE_MAPPING[sub_type](artist)


def generate_question_hits(artist: Artist):
    songs = repo_song.list_(
        filter_artist_id_in=[artist.id],
        filter_out_null_genius_pageviews=True,
        order_genius_pageviews=False,
        nbr_results=5,
        page_nbr=0,
    )

    for song in songs:
        if _check_exists(ResponseType.ARTIST, QuestionSubType.HIT, artist.id):
            continue

        question = Question(f'Quel est l\'auteur du titre "{song.title}" ?')
        question.type = ResponseType.ARTIST
        question.sub_type = QuestionSubType.HIT

        db.session.add(question)
        db.session.commit()

        question_response = QuestionResponse(
            question.id, artist.id, QuestionResponseStatus.CORRECT
        )

        db.session.add(question_response)
        db.session.commit()


def generate_question_artist_picture(artist: Artist):
    if artist.genius_profile_img_url is None or artist.genius_profile_img_url == "":
        return

    if _check_exists(ResponseType.ARTIST, QuestionSubType.ARTIST_PICTURE, artist.id):
        return

    question = Question(f"Qui est cet artiste ?")
    question.type = ResponseType.ARTIST
    question.sub_type = QuestionSubType.ARTIST_PICTURE
    question.picture = artist.genius_profile_img_url

    db.session.add(question)
    db.session.commit()

    question_response = QuestionResponse(
        question.id, artist.id, QuestionResponseStatus.CORRECT
    )

    db.session.add(question_response)
    db.session.commit()


def _check_exists(
    response_type: ResponseType,
    question_sub_type: QuestionSubType,
    true_response_id: int,
):
    return (
        repo_question.get(
            filter_type_in=[response_type],
            filter_sub_type_in=[question_sub_type],
            filter_true_response_id_in=[true_response_id],
        )
        is not None
    )


RESPONSE_SUB_TYPE_MAPPING = {
    QuestionSubType.HIT: generate_question_hits,
    QuestionSubType.ARTIST_PICTURE: generate_question_artist_picture,
}
