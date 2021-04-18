from app.crawlers.base_crawler import BaseCrawler


class AlbumCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(["albums"])
