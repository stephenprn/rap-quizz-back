from typing import List

from sqlalchemy.orm import load_only

from app.models import User, UserRole
from app.shared.db import db
from app.repositories.repository_artist import ArtistRepository

repo_artist = ArtistRepository()


def get_artists_list(nbr_results: int, page_nbr: int):
    return repo_artist.list_(
        nbr_results=nbr_results,
        page_nbr=page_nbr,
        with_nbr_results=True,
        order_update_date=False,
    )
