from typing import Optional, Callable, List
from flask import request, abort, json
from functools import wraps

from app.models import UserRole
from app.utils.utils_json import default_handler
from app.services import service_auth

# if nbr_results_default is specified, we try to get nbr_results


def pagination(nbr_results_default=None) -> Callable:
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                page_nbr = int(request.args.get("page_nbr"))

                if page_nbr is None or page_nbr == "":
                    page_nbr = 0
            except Exception:
                abort(400, "Page number is required: page_nbr")

            if nbr_results_default is not None:
                try:
                    nbr_results = int(request.args.get("nbr_results"))

                    if nbr_results is None or nbr_results == "":
                        nbr_results = nbr_results_default
                except Exception:
                    nbr_results = nbr_results_default

                kwargs["nbr_results"] = nbr_results

            kwargs["page_nbr"] = page_nbr

            return function(*args, **kwargs)

        wrapper.__name__ = function.__name__
        return wrapper

    return decorator


# convert objects or lists to json


def to_json(paginated=False) -> Callable:
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            res = function(*args, **kwargs)
            res_dict = convert_to_dict(res, paginated)
            return convert_to_json(res_dict)

        wrapper.__name__ = function.__name__
        return wrapper

    return decorator


def has_role(roles: List[UserRole]):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if service_auth.get_current_identity().role not in roles:
                abort(403, "You are not allowed to access this resource")

            return function(*args, **kwargs)

        wrapper.__name__ = function.__name__
        return wrapper

    return decorator


def convert_to_dict(res, paginated=False) -> Optional[dict]:
    if paginated:
        data = res["data"]
    else:
        data = res

    if isinstance(data, list):
        data_dict = [elt.to_dict() for elt in data]
    else:
        data_dict = data.to_dict()

    if not paginated:
        return data_dict
    else:
        return {"total": res["total"], "data": data_dict}

    return None


def convert_to_json(res_dict, paginated=False) -> Optional[str]:
    if res_dict is not None:
        return json.dumps(res_dict, default=default_handler, sort_keys=True)

    return None
