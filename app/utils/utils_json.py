import datetime
from enum import Enum
from flask.json import JSONEncoder

def default_handler(x) -> str:
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    elif isinstance(x, Enum):
        return x.name

    raise TypeError("Unknown type")

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return default_handler(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)