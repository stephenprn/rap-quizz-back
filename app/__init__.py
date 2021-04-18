from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_alembic import Alembic

from os import environ
from dotenv import load_dotenv

from app.utils.utils_json import CustomJSONEncoder
from app.shared.db import db
from app.shared.socketio import socketio
from app.services.service_admin import init_users

current_app = None


def create_app():
    """Load env parameters"""
    load_dotenv()

    """Construct the core application."""
    app = Flask(__name__)

    app.json_encoder = CustomJSONEncoder

    app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("SQLALCHEMY_DATABASE_URI")
    app.config["SECRET_KEY"] = environ.get("SECRET_KEY")
    app.config["JWT_AUTH_URL_RULE"] = environ.get("JWT_AUTH_URL_RULE")
    app.config["JWT_AUTH_USERNAME_KEY"] = environ.get("JWT_AUTH_USERNAME_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(
        environ.get("JWT_ACCESS_TOKEN_EXPIRES", 1800)
    )
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = int(
        environ.get("JWT_REFRESH_TOKEN_EXPIRES", 259200)
    )
    app.config["SQLALCHEMY_ECHO"] = environ.get("SQLALCHEMY_ECHO") == "true"

    db.init_app(app)

    @app.before_first_request
    def before_first_request():
        if app.env == "development":
            from app.setup_dev import init_test_users, init_test_questions

            init_test_users()
            init_test_questions()

    with app.app_context():
        # blueprints init
        from app.routes.application_auth import application_auth
        from app.routes.application_quiz import application_quiz
        from app.routes.application_response import application_response
        from app.routes.application_question import application_question
        from app.routes.application_profile import application_profile

        app.register_blueprint(application_auth, url_prefix="/auth")
        app.register_blueprint(application_quiz, url_prefix="/quiz")
        app.register_blueprint(application_response, url_prefix="/response")
        app.register_blueprint(application_question, url_prefix="/question")
        app.register_blueprint(application_profile, url_prefix="/profile")

        db.create_all()  # Create sql tables for our data models
        init_users()

        CORS(app)
        JWTManager(app)

        alembic = Alembic()
        # alembic.rev_id = lambda: datetime.utcnow().timestamp()
        alembic.init_app(app)

        socketio.init_app(app, cors_allowed_origins="*")


        global current_app
        current_app = app

        return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
