from typing import List

from app.shared.db import db
from app.models import Artist, QuestionSubType, ResponseType, Question, QuestionResponse, QuestionResponseStatus
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
    songs = repo_song.get_top_by_artist_id(artist.id)

    for song in songs:
        if repo_question.get(type_=ResponseType.ARTIST, sub_type=QuestionSubType.HIT, true_response_id=song.id) is not None:
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


RESPONSE_SUB_TYPE_MAPPING = {
    QuestionSubType.HIT: generate_question_hits
}
