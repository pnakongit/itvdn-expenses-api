from flask import Flask
from flask_swagger import swagger


def create_swagger_spec(app: Flask) -> dict:
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "My API"
    swag["securityDefinitions"] = {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
        }
    }
    swag["definitions"] = {
        "Greeting": {
            "type": "object",
            "discriminator": "greetingType",
            "properties": {"message": {"type": "string"}},
            "example": {"message": "Hello from Expenses API!"},
        },
        "ExpenseIn": {
            "type": "object",
            "discriminator": "expenseInType",
            "properties": {
                "title": {"type": "string"},
                "amount": {"type": "number"}
            },
            "example": {
                "title": "I'm your expense", "amount": 5.21
            },
        },
        "ExpenseOut": {
            "allOf": [
                {"$ref": "#/definitions/ExpenseIn"},
                {
                    "properties": {
                        "id": {"type": "integer"},
                        "user_id": {"type": "integer"},
                    },
                    "example": {
                        "id": 1,
                        "user_id": 1,
                    }
                }
            ]
        },
        "ExpensePatch": {
            "type": "object",
            "discriminator": "expensePatchType",
            "properties": {
                "title": {"type": "string"},
                "amount": {"type": "number"}
            },
            "required": [],
            "example": {
                "title": "I'm your expense", "amount": 5.21
            },
        },
        "UserIn": {
            "type": "object",
            "discriminator": "UserInType",
            "properties": {
                "username": {
                    "type": "string",
                    "unique": True,
                    "minLength": 4,
                    "maxLength": 20,
                },
                "password": {
                    "type": "string",
                    "minLength": 4,
                }
            },
            "example": {
                "username": "<USERNAME>",
                "password": "<PASSWORD>"
            },
        },
        "LoginIn": {
            "allOf": [
                {"$ref": "#/definitions/UserIn"},
                {
                    "discriminator": "LoginType",
                    "properties": {
                        "username": {
                            "type": "string",
                            "minLength": 4,
                            "maxLength": 20,
                        },
                    }
                }
            ]
        },
        "LoginOut": {
            "type": "object",
            "discriminator": "LoginType",
            "properties": {
                "access_token": {"type": "string"},
                "refresh_token": {"type": "string"},
            },
            "example": {
                "access_token": "YOUR ACCESS TOKEN",
                "refresh_token": "YOUR REFRESH TOKEN",
            },
        },
        "UserOut": {
            "type": "object",
            "discriminator": "UserOutType",
            "properties": {
                "id": {
                    "type": "integer"
                },
                "username": {
                    "type": "string"
                },
            },
            "example": {
                "id": 1,
                "username": "YOUR_USERNAME",
            },
        },
        "NotFound": {
            "type": "object",
            "discriminator": "notFoundType",
            "properties":
                {"error": {
                    "type": "object",
                    "discriminator": "errorType",
                    "properties": {
                        "code": {"type": "integer"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                    }
                }},
            "example": {
                "error": {
                    "code": 404,
                    "name": "Not Found",
                    "description": "Not found"
                },
            },
        },
    }

    return swag
