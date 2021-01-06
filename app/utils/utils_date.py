from datetime import datetime

DEFAULT_FORMAT = "%d/%m/%Y"


def get_current_date() -> datetime:
    return datetime.now()


def get_current_date_string(date_format: str = DEFAULT_FORMAT) -> str:
    return get_current_date().strftime(date_format)


def get_current_datetime_string() -> str:
    return get_current_date().isoformat()
