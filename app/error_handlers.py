from flask import Response, jsonify
from werkzeug.exceptions import NotFound, Unauthorized
from marshmallow import ValidationError


def handle_not_fount(e: NotFound) -> (Response, int):
    data = {
        "error": {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    }
    return jsonify(data), e.code


def handle_schema_errors(e: ValidationError) -> (Response, int):
    return jsonify(errors=e.messages_dict), 400


def handle_unauthorized(e: Unauthorized) -> (Response, int):
    data = {
        "error": {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    }
    return jsonify(data), e.code
