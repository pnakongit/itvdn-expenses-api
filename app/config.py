import datetime
import os


class BaseConfig:

    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SPEC_URL = "/spec"
    BASE_SWAGGER_URL = "/swagger"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(hours=1)
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=5)


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    SERVER_NAME = "localhost:5000"
