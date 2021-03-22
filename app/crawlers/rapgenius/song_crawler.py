from app.crawlers.base_crawler import BaseCrawler
from app.models import Song
from app.repositories.repository_artist import ArtistRepository


class SongCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(['songs'])
        self.model = Song
        self.base_path = 'response.song'


class ArtistSongsCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(['artists', 'songs'], True)
        self.model = Song
        self.base_path = 'response.songs'
        self.artist_repo = ArtistRepository()

    def get(self, ids_: List[int], text_format: str = 'plain'):
        artist = self.artist_repo.get_by_genius_id(ids_[0])

        if artist == None:
            raise ValueError('Artist does not exist')

        res_dict = self.get_dict(ids_, text_format)
        return [self.model.from_dict(r, artist) for r in res_dict]


if __name__ == '__main__':
    print(ArtistSongsCrawler().get([16775]))
