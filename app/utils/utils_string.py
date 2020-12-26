from flask import abort
import unicodedata
import re
import string
import random
from uuid import uuid4

RANDOM_CHARS = string.ascii_uppercase + string.ascii_lowercase + string.digits


def normalize_string(text: str, replace_spaces: str = " "):
    try:
        text = unicode(text, "utf-8")
    except NameError:  # unicode is a default on python 3
        pass

    text = (
        unicodedata.normalize("NFD", text)
        .encode("ascii", "ignore")
        .decode("utf-8")
        .lower()
    )

    sub_texts = []

    try:
        for sub in text.split(" "):
            sub_texts.append(re.sub("[^A-Za-z0-9]+", "", sub))
    except Exception as e:
        pass

    return replace_spaces.join(sub_texts)


def check_length(text: str, name: str, min_length: int, max_length: int = None):
    if text == None:
        abort(400, "{} must be specified".format(name, str(min_length)))

    if len(text) < min_length:
        abort(
            400, "{} must be at least {} characters long".format(
                name, str(min_length))
        )

    if max_length != None and len(text) > max_length:
        abort(
            400,
            "{} must be no more than {} characters long".format(
                name, str(min_length)),
        )


def generate_uuid():
    return str(uuid4())


def generate_random_string(length: int):
    return ''.join(random.choices(RANDOM_CHARS, k=length))


if __name__ == "__main__":
    print(normalize_string("Héùlàïo iM'ka +=$*-éàççàu(çà!§-", "-"))
