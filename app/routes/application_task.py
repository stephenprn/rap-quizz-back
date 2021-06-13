import threading
import time

from flask import Blueprint, abort, current_app
from flask.helpers import url_for
from app.utils.utils_query import async_tasks

from app.utils import utils_date

application_task = Blueprint("task", __name__)


@application_task.before_app_first_request
def before_first_request():
    """Start a background thread that cleans up old tasks."""

    def clean_old_tasks():
        """
        This function cleans up old tasks from our in-memory data structure.
        """
        global async_tasks

        while True:
            # Only keep tasks that are running or that finished less than 10
            # minutes ago.
            ten_min_ago = utils_date.get_current_date() - 10 * 60
            async_tasks = {
                id: task
                for id, task in async_tasks.items()
                if "t" not in task or task["t"] > ten_min_ago
            }
            time.sleep(60)

    if not current_app.config["TESTING"]:
        thread = threading.Thread(target=clean_old_tasks)
        thread.start()


@application_task.route("/status/<id>", methods=["GET"])
def get_status(id):
    """
    Return status about an asynchronous task. If this request returns a 202
    status code, it means that task hasn't finished yet. Else, the response
    from the task is returned.
    """
    task = async_tasks.get(id)
    if task is None:
        abort(404)
    if "rv" not in task:
        return "", 202, {"Location": url_for("tasks.get_status", id=id)}
    return task["rv"]
