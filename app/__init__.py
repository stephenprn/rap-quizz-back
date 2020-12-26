from flask import Flask
from flask_cors import CORS
from flask_jwt import JWT

from os import environ
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv

from app.shared.db import db
from app.shared.socketio import socketio
from app.services.service_admin import init_users
from app.services.service_auth import authenticate, identity


def create_app():
    """Load env parameters"""
    load_dotenv()

    """Construct the core application."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("SQLALCHEMY_DATABASE_URI")
    app.config["SECRET_KEY"] = environ.get("SECRET_KEY")
    app.config["JWT_AUTH_URL_RULE"] = environ.get("JWT_AUTH_URL_RULE")
    app.config["JWT_AUTH_USERNAME_KEY"] = environ.get("JWT_AUTH_USERNAME_KEY")

    db.init_app(app)

    @app.before_first_request
    def before_first_request():
        if app.env == 'development':
            from app.setup_dev import init_test_users, init_test_questions

            init_test_users()
            init_test_questions()

    with app.app_context():
        # blueprints init
        from app.routes.application_auth import application_auth
        from app.routes.application_quiz import application_quiz
        from app.routes.application_response import application_response
        from app.routes.application_question import application_question

        app.register_blueprint(application_auth, url_prefix="/auth")
        app.register_blueprint(application_quiz, url_prefix="/quiz")
        app.register_blueprint(application_response, url_prefix="/response")
        app.register_blueprint(application_question, url_prefix="/question")

        db.create_all()  # Create sql tables for our data models
        init_users()

        CORS(app)
        JWT(app, authenticate, identity)
        
        socketio.init_app(app, cors_allowed_origins="*")

        from app import events
        
        return app
