from typing import Any, Dict, Optional
from typing_extensions import TypedDict


class FilterText:
    text: str
    ignore_case: bool
    partial_match: bool

    def __init__(
        self,
        text: str,
        ignore_case: Optional[bool] = False,
        partial_match: Optional[bool] = False,
    ):
        self.text = text
        self.ignore_case = ignore_case
        self.partial_match = partial_match


class FilterInt:
    min_value: int
    max_value: int
    min_strict: bool
    max_strict: bool

    def __init__(
        self,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        min_strict: Optional[bool] = True,
        max_strict: Optional[bool] = True,
    ):
        self.min_value = min_value
        self.max_value = max_value
        self.min_strict = min_strict
        self.max_strict = max_strict


class ArgsKwargs(TypedDict):
    args: Optional[Dict[str, Any]]
    kwargs: Optional[Dict[str, Any]]
