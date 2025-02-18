from flask import Flask
from flask_swagger import swagger


def create_swagger_spec(app: Flask) -> dict:
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "My API"
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
                }
            },
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
    }
    return swag
