from typing import List

from app.utils import utils_json
from app.crawlers.base_crawler import BaseCrawler
from app.models import Song
from app.repositories.repository_artist import ArtistRepository


class SongCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(["songs"])
        self.model = Song
        self.base_path = "response.song"


class ArtistSongsCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(["artists", "songs"], True)
        self.model = Song
        self.base_path = "response.songs"
        self.artist_repo = ArtistRepository()

    def get(self, ids_: List[int], text_format: str = "plain"):
        artist = self.artist_repo.get(filter_genius_id_in=[ids_[0]])

        if artist == None:
            raise ValueError("Artist does not exist")

        page = 1
        res = []

        while True:
            res_dict = self._get_dict(
                ids_, text_format, additional_params={"page": page}
            )

            next_page = utils_json.get_nested_field(res_dict, "response.next_page")
            res_dict = utils_json.get_nested_field(res_dict, self.base_path)
            res += [self.model.from_dict(r, artist) for r in res_dict]

            if next_page == None:
                break

            page = next_page

        return res


if __name__ == "__main__":
    print(ArtistSongsCrawler().get([16775]))
