from flask import Flask
from flask_cors import CORS
from flask_jwt import JWT

from os import environ
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv

from app.shared.db import db
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

        # @app.errorhandler(Exception)
        # def handle_error(e):
        #     code = 500

        #     if isinstance(e, HTTPException):
        #         code = e.code

        #     try:
        #         exc_type, exc_obj, exc_tb = sys.exc_info()
        #         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #         import pdb; pdb.set_trace()
        #         print(e)
        #         print(exc_type, fname, exc_tb.tb_lineno)

        #         return dumps(str(e.description)), code
        #     except Exception:
        #         return dumps(str(e)), code

        return app
