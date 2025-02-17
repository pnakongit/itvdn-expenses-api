from flask import Blueprint, Response, request, jsonify
from werkzeug.security import generate_password_hash

from app.db import db, User
from app.schemas import user_schema

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["POST"])
def register() -> (Response, int):
    json_data = request.get_json()

    data = user_schema.load(json_data)

    user = User(
        username=data["username"],
        password=generate_password_hash(data["password"]),
    )

    db.session.add(user)
    db.session.commit()

    return jsonify(user_schema.dump(user)), 201
