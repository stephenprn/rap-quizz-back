from flask import request, abort, json
from functools import wraps

from app.utils.utils_json import default_handler

# if nbr_results_default is specified, we try to get nbr_results


def pagination(nbr_results_default=None):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                page_nbr = int(request.args.get("page_nbr"))

                if page_nbr == None or page_nbr == "":
                    page_nbr = 0
            except Exception as e:
                abort(400, "Page number is required: page_nbr")

            if nbr_results_default != None:
                try:
                    nbr_results = int(request.args.get("nbr_results"))

                    if nbr_results == None or nbr_results == "":
                        nbr_results = nbr_results_default
                except Exception as e:
                    nbr_results = nbr_results_default

                kwargs["nbr_results"] = nbr_results

            kwargs["page_nbr"] = page_nbr

            return function(*args, **kwargs)

        wrapper.__name__ = function.__name__
        return wrapper

    return decorator


# convert objects or lists to json


def to_json(paginated=False):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            res = function(*args, **kwargs)
            res_dict = convert_to_dict(res, paginated)
            return convert_to_json(res_dict)

        wrapper.__name__ = function.__name__
        return wrapper

    return decorator


def convert_to_dict(res, paginated=False):
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


def convert_to_json(res_dict, paginated=False):
    if res_dict != None:
        return json.dumps(res_dict, default=default_handler, sort_keys=True)

    return None
