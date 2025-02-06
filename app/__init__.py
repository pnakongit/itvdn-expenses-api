from flask import Flask, Response, jsonify
from werkzeug.exceptions import NotFound

DATABASE_URI = "sqlite:///expenses.sqlite3"
SPEC_URL = "/spec"
BASE_SWAGGER_URL = "/swagger"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI

    from app.db import db
    db.init_app(app)

    from app.expenses import bp as expenses_bp
    from app.swagger_bp import swagger_ui_bd

    app.register_blueprint(expenses_bp)
    app.register_blueprint(swagger_ui_bd)

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

    from app.error_handlers import handle_not_fount
    app.register_error_handler(NotFound, handle_not_fount)

    with app.app_context():
        db.create_all()

    return app
