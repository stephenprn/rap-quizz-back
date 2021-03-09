from app.crawlers.base_crawler import BaseCrawler
from app.models.artist import Artist

class ArtistCrawler(BaseCrawler):
    def __init__(self):
        super().__init__('artists')
        self.model = Artist
        self.base_path = 'response.artist'

if __name__ == '__main__':
    print(ArtistCrawler().get(16775))