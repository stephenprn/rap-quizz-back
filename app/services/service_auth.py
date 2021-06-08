import random

from flask import abort
from flask_jwt_extended import (
    get_jwt_identity,
)
import app.models
from app.shared.db import db
from app.utils.utils_hash import check_password, hash_password
from app.utils.utils_string import check_length

USERNAME_MIN_LENGTH = 4
USERNAME_MAX_LENGTH = 100

PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 20

USER_COLORS = [
    "#D50000",
    "#C51162",
    "#AA00FF",
    "#6200EA",
    "#304FFE",
    "#2962FF",
    "#0091EA",
    "#00B8D4",
    "#00BFA5",
    "#00C853",
    "#64DD17",
    "#AEEA00",
    "#FFD600",
    "#FFAB00",
    "#FF6D00",
    "#DD2C00",
    "#3E2723",
    "#212121",
    "#263238",
]


def register(email: str, username: str, password: str) -> None:
    check_length(
        password,
        "Password",
        PASSWORD_MIN_LENGTH,
        PASSWORD_MAX_LENGTH)
    check_length(
        username,
        "Username",
        USERNAME_MIN_LENGTH,
        USERNAME_MAX_LENGTH)

    email = email.lower()

    email_exists = (
        db.session.query(app.models.User.id)
        .filter(app.models.User.email == email)
        .scalar()
        is not None
    )

    if email_exists:
        abort(409, "This email is already registered")

    username_exists = (
        db.session.query(app.models.User.id)
        .filter(app.models.User.username == username)
        .scalar()
        is not None
    )

    if username_exists:
        abort(409, "This username is already taken")

    user = app.models.User(
        username,
        email,
        password,
        color=random.choice(USER_COLORS))

    db.session.add(user)
    db.session.commit()


def check_username(username: str) -> None:
    username_exists = (
        db.session.query(app.models.User.id)
        .filter(app.models.User.username == username)
        .scalar()
        is not None
    )

    if username_exists:
        abort(409, "This username is already taken")


def has_role(role: app.models.UserRole = None):
    user = get_current_identity()

    if user.role >= role:
        return True

    return False


# flask_jwt_extended functions


def authenticate(email: str, password: str, with_id: bool = True) -> dict:
    hash_password(password)
    email = email.lower()

    user = db.session.query(app.models.User).filter_by(email=email).first()

    if user is None:
        return None

    if not check_password(password, user.salt, user.password):
        return None

    return {
        "username": user.username,
        "uuid": user.uuid,
        "id": user.id,
        "color": user.color,
    }


def get_current_identity() -> app.models.User:
    identity_dict = get_jwt_identity()

    user = (
        db.session.query(app.models.User)
        .filter_by(uuid=identity_dict.get("uuid"))
        .first()
    )

    if user is None:
        abort(403, "Invalid token")

    return user
