import datetime
from enum import Enum


def default_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    elif isinstance(x, Enum):
        return x.name

    raise TypeError("Unknown type")
