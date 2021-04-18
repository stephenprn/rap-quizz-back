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


def generate_question_artist(artist: Artist, sub_types: List[QuestionSubType] = None):
    if sub_types is not None:
        for sub_type in sub_types:
            RESPONSE_SUB_TYPE_MAPPING[sub_type]()
    else:
        for sub_types in QuestionSubType:
            RESPONSE_SUB_TYPE_MAPPING[sub_type]()


def generate_question_hits(artist: Artist):
    songs = repo_song.list_(
        filter_artist_id_in=[artist.id],
        filter_out_null_genius_pageviews=True,
        order_genius_pageviews=False,
        nbr_results=5,
        page_nbr=0,
    )

    for song in songs:
        if repo_question.get(
            filter_type_in=[ResponseType.ARTIST],
            filter_sub_type_in=[QuestionSubType.HIT],
            filter_true_response_id_in=[song.id],
        ):
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


RESPONSE_SUB_TYPE_MAPPING = {QuestionSubType.HIT: generate_question_hits}
