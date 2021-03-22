from enum import Enum
import requests
import os
from abc import ABC
from typing import List, Optional

from app.utils import utils_json


class BaseCrawler(ABC):
    def __init__(self, resources: List[str], multiple: bool = False, nbr_retries: int = 5):
        self.resources = resources
        self.multiple = multiple
        self.nbr_retries = nbr_retries
    
    def get(self, ids_: List[int], text_format: str = 'plain'):
        res_dict = self.get_dict(ids_, text_format)

        if not self.multiple:
            return self.model.from_dict(res_dict)
        else:
            return [self.model.from_dict(r) for r in res_dict]

    def _get_dict(self, ids_: List[int], text_format: str = 'plain') -> Optional[dict]:
        try_nbr = 0

        while try_nbr < self.nbr_retries:
            r = requests.get(self._build_url(ids_), params={
                'text_format': text_format
            }, headers={
                'Authorization': f'Bearer {os.environ.get("RAPGENIUS_BEARER_TOKEN")}'
            })

            if r.status_code == 200:
                return utils_json.get_nested_field(
                    r.json(), self.base_path)

            try_nbr += 1

        raise ValueError('Number of retries reached')

    def _build_url(self, ids_: List[int]):
        # we can have res1/id1/res2 or res1/id1/res2/id2
        if len(ids_) < len(self.resources) - 1:
            raise ValueError('Resources and ids_ must have the same length')

        url = 'http://api.genius.com/'

        for i, res in enumerate(self.resources):
            url += res + '/'
            
            if i < len(ids_):
                url += str(ids_[i]) + '/'
                
        return url[:-1]


if __name__ == '__main__':
    print(BaseCrawler(['album']).get_dict())
