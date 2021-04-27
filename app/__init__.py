from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_alembic import Alembic
from flask_migrate import Migrate

from os import environ
from dotenv import load_dotenv

from app.constants import Environment
from app.config import configs_env_mapping
from app.utils.utils_json import CustomJSONEncoder
from app.shared.db import db
from app.shared.socketio import socketio
from app.services.service_admin import init_users

current_app = None
migrate = None
alembic = None


def create_app():
    global migrate
    global current_app
    global alembic

    """Load env parameters"""
    load_dotenv()

    environment = Environment[environ.get('ENVIRONMENT')]

    """Construct the core application."""
    app = Flask(__name__)
    app.config.from_object(configs_env_mapping[environment])
    app.json_encoder = CustomJSONEncoder

    migrate = Migrate(app, db)

    db.init_app(app)

    @app.before_first_request
    def before_first_request():
        if environment == Environment.development:
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

        current_app = app

        return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
