from typing import Optional
from werkzeug import exceptions

from app.shared.db import db
from app.services import service_response
from app.models import Artist
from app.repositories import ArtistRepository, SongRepository

from app.crawlers.rapgenius import (
    ArtistCrawler,
    ArtistSongsCrawler,
)

repo_artist = ArtistRepository()
repo_song = SongRepository()


def crawl_artist_full(id_: int, nbr_songs_max: Optional[int] = 5) -> Artist:
    artist = repo_artist.get(filter_genius_id_in=[id_])

    if not artist:
        artist = ArtistCrawler().get([id_])

    try:
        service_response.add(artist)
    except exceptions.Conflict:
        pass

    songs = ArtistSongsCrawler().get([id_])

    songs = sorted(songs, lambda song: -song.genius_pageviews)

    for song in songs[nbr_songs_max:]:
        db.session.delete(song)

    songs = songs[:nbr_songs_max]

    for song in songs:
        try:
            service_response.add(song)
        except exceptions.Conflict:
            pass

    return artist


if __name__ == "__main__":
    crawl_artist_full(19217)
