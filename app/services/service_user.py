from flask import abort

from app.shared.db import db

from app.models.user import UserRole
from app.repositories import UserRepository
from app.services import service_auth


repo_user = UserRepository()


def list_(nbr_results: int, page_nbr: int, hidden: bool = None):
    return repo_user.list_(
        nbr_results=nbr_results,
        page_nbr=page_nbr,
        filter_hidden=hidden,
        order_creation_date=False,
        with_nbr_results=True,
    )


def edit(user_uuid: str, role: UserRole = None):
    user = repo_user.get(filter_uuid_in=[user_uuid])

    if user.role >= service_auth.get_current_identity().role:
        abort(400, "You cannot edit a user with a role higher than yours")

    if role is not None:
        if service_auth.get_current_identity().role < role:
            abort(400, "You cannot set a role higher than yours")

        user.role = role

    db.session.commit()
