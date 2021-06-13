from typing import List

from flask import abort

from app.shared.db import db
from app.models import (
    Artist,
    QuestionSubType,
    ResponseType,
    Question,
    QuestionResponse,
    QuestionResponseStatus,
)
from app.repositories import SongRepository, QuestionRepository, ArtistRepository

repo_song = SongRepository()
repo_question = QuestionRepository()
repo_artist = ArtistRepository()


def generate_questions_artist(
    artist: Artist = None,
    artist_uuid: str = None,
    sub_types: List[QuestionSubType] = None,
) -> int:
    if artist is None:
        artist = repo_artist.get(filter_uuid_in=[artist_uuid])

        if artist is None:
            abort(404, "Artist not found")

    if sub_types is None:
        sub_types = QuestionSubType

    nbr_generated = 0

    for sub_type in sub_types:
        if RESPONSE_SUB_TYPE_MAPPING.get(sub_type):
            nbr_generated += RESPONSE_SUB_TYPE_MAPPING[sub_type](artist)

    return nbr_generated


def generate_question_hits(artist: Artist):
    songs = repo_song.list_(
        filter_artist_id_in=[artist.id],
        filter_out_null_genius_pageviews=True,
        order_genius_pageviews=False,
        nbr_results=5,
        page_nbr=0,
    )

    nbr_generated = 0

    for song in songs:
        if _check_exists(ResponseType.ARTIST, QuestionSubType.HIT, artist.id):
            continue

        question = Question(f'Quel est l\'auteur du titre "{song.title}" ?')
        question.type = ResponseType.ARTIST
        question.sub_type = QuestionSubType.HIT

        db.session.add(question)
        nbr_generated += 1

        db.session.commit()

        question_response = QuestionResponse(
            question.id, artist.id, QuestionResponseStatus.CORRECT
        )

        db.session.add(question_response)
        db.session.commit()

    return nbr_generated


def generate_question_artist_picture(artist: Artist):
    nbr_generated = 0

    if artist.genius_profile_img_url is None or artist.genius_profile_img_url == "":
        return nbr_generated

    if _check_exists(
            ResponseType.ARTIST,
            QuestionSubType.ARTIST_PICTURE,
            artist.id):
        return nbr_generated

    question = Question(f"Qui est cet artiste ?")
    question.type = ResponseType.ARTIST
    question.sub_type = QuestionSubType.ARTIST_PICTURE
    question.picture = artist.genius_profile_img_url

    db.session.add(question)
    nbr_generated += 1

    db.session.commit()

    question_response = QuestionResponse(
        question.id, artist.id, QuestionResponseStatus.CORRECT
    )

    db.session.add(question_response)
    db.session.commit()

    return nbr_generated


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
