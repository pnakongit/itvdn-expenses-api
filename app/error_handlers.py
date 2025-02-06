from flask import Response, jsonify
from werkzeug.exceptions import NotFound


def handle_not_fount(e: NotFound) -> (Response, int):
    data = {
        "error": {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    }
    return jsonify(data), e.code
