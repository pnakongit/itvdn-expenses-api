import datetime

from flask import Flask, Response, jsonify
from werkzeug.exceptions import NotFound, Unauthorized, Forbidden
from marshmallow import ValidationError

DATABASE_URI = "sqlite:///expenses.sqlite3"
SPEC_URL = "/spec"
BASE_SWAGGER_URL = "/swagger"
JWT_SECRET_KEY = "Test JWT"
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(hours=1)
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=5)

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = JWT_REFRESH_TOKEN_EXPIRES
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = JWT_ACCESS_TOKEN_EXPIRES

    from app.db import db
    from app.migrate import migrate
    from app.jwt import jwt

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    jwt.init_app(app)

    from app.expenses import bp as expenses_bp
    from app.swagger_bp import swagger_ui_bd
    from app.auth import bp as auth_bp

    app.register_blueprint(expenses_bp)
    app.register_blueprint(swagger_ui_bd)
    app.register_blueprint(auth_bp)

    from app.swagger_utils import create_swagger_spec

    @app.route(SPEC_URL)
    def spec() -> Response:
        swag = create_swagger_spec(app)
        return jsonify(swag)

    @app.route('/')
    def index() -> (dict, int):
        """
        Return a greeting message
        Test endpoint to see if it works
        ---
        tags:
        - tests
        responses:
          200:
            description: Greeting
            schema:
              $ref: "#definitions/Greeting"
        """
        return {"message": "Hello from Expenses API!"}, 200

    from app.error_handlers import (
        handle_not_fount,
        handle_schema_errors,
        handle_unauthorized,
        handle_forbidden
    )

    app.register_error_handler(NotFound, handle_not_fount)
    app.register_error_handler(ValidationError, handle_schema_errors)
    app.register_error_handler(Unauthorized, handle_unauthorized)
    app.register_error_handler(Forbidden, handle_forbidden)
    return app
