from flask import Blueprint, request, json, Response
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
)

from app.shared.db import db
from app.services import service_auth

application_auth = Blueprint("application_auth", __name__)

# /login endpoint is reserved and managed by flask_jwt_extended


@application_auth.route("/")
def hello():
    return "hello auth"


@application_auth.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    user_dict = service_auth.authenticate(email, password)

    if user_dict == None:
        abort(400, "Invalid credentials")

    return json.dumps(
        {
            "access_token": create_access_token(identity=user_dict),
            "refresh_token": create_refresh_token(identity=user_dict),
            "user": {
                "username": user_dict["username"],
                "uuid": user_dict["uuid"]
            },
        }
    )


@application_auth.route("/refresh")
@jwt_refresh_token_required
def refresh():
    user_dict = get_jwt_identity()
    return json.dumps({"access_token": create_access_token(identity=user_dict)})


@application_auth.route("/register", methods=["POST"])
def register():
    email = request.json.get("email")
    username = request.json.get("username")
    password = request.json.get("password")

    service_auth.register(email, username, password)

    return Response(status=200)


# this endpoint will return a 409 code if username is taken, 200 if not


@application_auth.route("/check-username", methods=["POST"])
def check_username():
    username = request.json.get("username")
    service_auth.check_username(username)

    return Response(status=200)


# this endpoint will return a 401 code if token is invalid, 200 if valid


@application_auth.route("/check-logged")
@jwt_required
def check_logged():
    return Response(status=200)
