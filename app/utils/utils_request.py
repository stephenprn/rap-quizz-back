from functools import wraps
import threading
import uuid

from flask import current_app, request
from flask.helpers import url_for
from werkzeug.exceptions import HTTPException, InternalServerError

from app.utils import utils_date
from app.shared.db import db

async_tasks = {}


def async_task(f):
    """
    This decorator transforms a sync route to asynchronous by running it
    in a background thread.
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        def task(app, environ):
            # Create a request context similar to that of the original request
            # so that the task can have access to flask.g, flask.request, etc.
            with app.request_context(environ):
                try:
                    # Run the route function and record the response
                    async_tasks[id]["rv"] = f(*args, **kwargs)
                except HTTPException as e:
                    async_tasks[id]["rv"] = current_app.handle_http_exception(
                        e)
                except Exception as e:
                    # The function raised an exception, so we set a 500 error
                    async_tasks[id]["rv"] = InternalServerError()
                    if current_app.debug:
                        # We want to find out if something happened so reraise
                        raise
                finally:
                    # We record the time of the response, to help in garbage
                    # collecting old tasks
                    async_tasks[id]["t"] = utils_date.get_current_date()

                    # close the database session
                    db.session.remove()

        # Assign an id to the asynchronous task
        id = uuid.uuid4().hex

        # Record the task, and then launch it
        async_tasks[id] = {
            "task": threading.Thread(
                target=task,
                args=(
                    current_app._get_current_object(),
                    request.environ,
                ),
            )
        }
        async_tasks[id]["task"].start()

        # Return a 202 response, with a link that the client can use to
        # obtain task status
        return "", 202, {"Location": url_for("task.get_status", id=id)}

    return wrapped
