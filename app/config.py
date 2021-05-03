from os import environ

from app.constants import Environment


class Config(object):
    DEBUG = False
    SECRET_KEY = environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    # This is just here to suppress a warning from SQLAlchemy as it will soon be removed
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_AUTH_URL_RULE = environ.get("JWT_AUTH_URL_RULE")
    JWT_AUTH_USERNAME_KEY = environ.get("JWT_AUTH_USERNAME_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = int(environ.get("JWT_ACCESS_TOKEN_EXPIRES", 1800))
    JWT_REFRESH_TOKEN_EXPIRES = int(environ.get("JWT_REFRESH_TOKEN_EXPIRES", 259200))

    LOG_TYPE = environ.get("LOG_TYPE", "stream")
    LOG_LEVEL = environ.get("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_ECHO = environ.get("SQLALCHEMY_ECHO", "true") == "true"


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = environ.get("SQLALCHEMY_ECHO", "false") == "true"


configs_env_mapping = {
    Environment.production: ProductionConfig,
    Environment.development: DevelopmentConfig,
}
