import scrapy
import json
from datetime import datetime


class AlbumsSpider(scrapy.Spider):
    name = "albums"
    MIN_YEAR = 2019

    # for the moment, we miss all non "<a>" albums
    __FIRST_MONTH_SELECTOR_XPATH = "//b[contains(text(), 'Janvier')]/following-sibling::a"
    __NOT_FOUND_SELECTOR = ".render_404"

    def __init__(self):
        self.__init_year()

    def start_requests(self):
        for url in self.__get_urls():
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if len(response.css(self.__NOT_FOUND_SELECTOR)) > 0:
            return

        res = []
        months_albums = response.xpath(self.__FIRST_MONTH_SELECTOR_XPATH)

        for node in months_albums:
            date_artist_album_node = node.xpath('.//span/text()')

            if len(date_artist_album_node) == 0:
                date_artist_album_node = node.xpath('/text()')

            date_artist_album = date_artist_album_node.get()

            # sometimes, the album is included in date_artist_album because not between <i> tag
            # check if <i> in date_artist_album

            album = node.xpath('.//i/text()').get()

            if album is not None:
                date_artist_album += album

            album_res = {
                "url": node.css('a::attr(href)').extract_first(),
            }

            if date_artist_album.startswith('* '):
                album_res["complete"] = False
                date_artist_album = date_artist_album[2:]
            elif date_artist_album.startswith('- '):
                album_res["complete"] = True
                date_artist_album = date_artist_album[2:]

            date_artist_album = date_artist_album.split(" - ", 1)
            date_artist = date_artist_album[0]

            if ' : ' in date_artist:
                date_artist = date_artist.split(' : ')

                album_res["artist"] = date_artist[1]
                album_res["date"] = date_artist[0] + \
                    '/' + str(self.current_year)
            else:
                album_res["artist"] = date_artist
                album_res["date"] = "unknown"

            album_res["album"] = date_artist_album[1]

            res.append(album_res)

        with open('data.json', 'w') as f:
            json.dump(res, f, ensure_ascii=False)

    def __get_urls(self):
        self.__init_year()

        while self.current_year > self.MIN_YEAR:
            url = "https://genius.com/Genius-france-discographie-rap-{}-annotated".format(
                str(self.current_year))
            yield url

            self.current_year -= 1

    def __init_year(self):
        self.current_year = datetime.now().year
