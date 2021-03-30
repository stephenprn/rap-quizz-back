from werkzeug import exceptions

from app.shared.db import db
from app.services import service_response
from app.models import Artist
from app.repositories import ArtistRepository

from app.crawlers.rapgenius import AlbumCrawler, ArtistCrawler, ArtistSongsCrawler, SongCrawler

repo_artist = ArtistRepository()

def crawl_artist_full(id_: int) -> Artist:
    if not repo_artist.get_by_genius_id(id_):
        artist = ArtistCrawler().get([id_])

    try:
        service_response.add(artist)
    except exceptions.Conflict:
        pass

    songs = ArtistSongsCrawler().get([id_])

    for song in songs:
        try:
            service_response.add(song)
        except exceptions.Conflict:
            pass

    return artist


if __name__ == '__main__':
    crawl_artist_full(19217)
