from flask import Blueprint, Response, request, jsonify
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.exceptions import Unauthorized
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.db import db, User
from app.schemas import user_schema, user_schema_login

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["POST"])
def register() -> (Response, int):
    """
    Register a user
    You can register a user with this endpoint

    ---
    tags:
      - auth
    parameters:
      - in: body
        name: Users
        description: Create a new user
        schema:
          $ref: "#definitions/UserIn"
        required: true
    responses:
      201:
        description: Created
        schema:
          $ref: "#definitions/UserOut"
    """

    json_data = request.get_json()

    data = user_schema.load(json_data)

    user = User(
        username=data["username"],
        password=generate_password_hash(data["password"]),
    )

    db.session.add(user)
    db.session.commit()

    return jsonify(user_schema.dump(user)), 201


@bp.route("/login", methods=["POST"])
def login() -> (Response, int):
    """
    Register a user
    You can register a user with this endpoint

    ---
    tags:
      - auth
    parameters:
      - in: body
        name: UserLogin
        description: Get access token and refresh token
        schema:
          $ref: "#definitions/LoginIn"
        required: true
    responses:
      201:
        description: Created
        schema:
          $ref: "#definitions/LoginOut"
    """
    json_data = request.get_json()
    data = user_schema_login.load(json_data)

    user = (
        db.session.query(User)
        .filter(User.username == data["username"])
        .one_or_none()
    )

    if not user or not user.check_password(data["password"]):
        raise Unauthorized(description="Incorrect credentials")

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify(
        access_token=access_token, refresh_token=refresh_token
    ), 201


@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh() -> (Response, int):
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token), 200
