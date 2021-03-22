from app.shared.db import db

from app.crawlers.rapgenius import AlbumCrawler, ArtistCrawler, ArtistSongsCrawler, SongCrawler


def crawl_artist_full(id_: int):
    artist = ArtistCrawler().get([id_])
    db.session.add(artist)
    db.session.commit()

    songs = ArtistSongsCrawler().get([id_])

    db.session.add_all(songs)
    db.session.commit()

if __name__ == '__main__':
    crawl_artist_full(74283)