from enum import Enum
import requests
import os
from abc import ABC

from app.utils import utils_json


class BaseCrawler(ABC):
    def __init__(self, resource: str, nbr_retries: int = 5):
        self.base_url = f'http://api.genius.com/{resource}/'
        self.nbr_retries = nbr_retries

    def get_dict(self, id_: int, text_format: str = 'plain'):
        try_nbr = 0

        while try_nbr < self.nbr_retries:
            r = requests.get(self.base_url + str(id_), params={
                'text_format': text_format
            }, headers={
                'Authorization': f'Bearer {os.environ.get("RAPGENIUS_BEARER_TOKEN")}'
            })

            if r.status_code == 200:
                return utils_json.get_nested_field(
                    r.json(), self.base_path)

            try_nbr += 1

    def get(self, id_: int, text_format: str = 'plain'):
        res_dict = self.get_dict(id_, text_format)
        return self.model.from_dict(res_dict)

    
