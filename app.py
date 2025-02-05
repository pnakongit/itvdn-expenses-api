from flask import Flask, request, jsonify
from flask.wrappers import Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.exceptions import NotFound
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint

DATABASE_URI = "sqlite:///expenses.sqlite3"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Expenses(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(50))
    amount: Mapped[float] = mapped_column(db.DECIMAL(precision=5, scale=2))

    def __repr__(self) -> str:
        return f"<{self.id} - {self.title}>"


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


@app.route("/expenses", methods=["POST"])
def create_expense() -> (Response, 201):
    """
    Create a new expense
    You can create a new expense by passing its title and amount in

    ---
    tags:
      - expenses
    parameters:
      - in: body
        name: Expenses
        description: Expenses title and amount
        schema:
          $ref: "#definitions/ExpenseIn"
        required: true
    responses:
      201:
        description: Created
        schema:
          $ref: "#definitions/ExpenseOut"
    """
    data = request.json

    expense = Expenses(title=data["title"], amount=data["amount"])
    db.session.add(expense)
    db.session.commit()

    return jsonify({
        "id": expense.id,
        "title": expense.title,
        "amount": expense.amount,
    }), 201


@app.route("/expenses", methods=["GET"])
def get_expenses() -> (Response, int):
    """
    Get all expenses
    Return a list of all expenses
    ---
    tags:
      - expenses
    responses:
      200:
        description: List of all expenses
        schema:
          type: array
          items:
            $ref: "#definitions/ExpenseOut"
    """
    expenses = Expenses.query.all()
    expenses = [
        {
            "id": expense.id,
            "title": expense.title,
            "amount": expense.amount,
        }
        for expense in expenses
    ]
    return jsonify(expenses), 200


@app.route("/expenses/<int:pk>", methods=["GET"])
def get_expense(pk: int) -> (Response, int):
    """
    Get an expense
    Return a single expense
    ---
    tags:
      - expenses
    parameters:
      - in: path
        name: pk
        type: integer
        description: Expense ID
        required: true
    responses:
      200:
        description: Return a single expense
        schema:
          $ref: "#definitions/ExpenseOut"
      404:
        description: Not found
        schema:
          $ref: "#definitions/NotFound"
    """
    expense = db.get_or_404(Expenses, pk, description="Expense not found")
    return jsonify({
        "id": expense.id,
        "title": expense.title,
        "amount": expense.amount,
    }), 200


@app.route("/expenses/<int:pk>", methods=["PATCH"])
def update_expense(pk: int) -> (Response, int):
    expense = db.get_or_404(Expenses, pk, description="Expense not found")
    expense.title = request.json.get("title", expense.title)
    expense.amount = request.json.get("amount", expense.amount)
    db.session.commit()

    return jsonify({
        "id": expense.id,
        "title": expense.title,
        "amount": expense.amount,
    }), 200


@app.route("/expenses/<int:pk>", methods=["DELETE"])
def delete_expense(pk: int) -> (Response, int):
    expense = db.get_or_404(Expenses, pk, description="Expense not found")
    db.session.delete(expense)
    db.session.commit()

    return "", 204


@app.errorhandler(NotFound)
def handle_not_fount(e: NotFound) -> (Response, int):
    data = {
        "error": {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    }
    return jsonify(data), e.code


@app.route("/spec")
def spec() -> Response:
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
                    },
                    "example": {
                        "id": 1,
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
    }
    return jsonify(swag)


swagger_ui_bd = get_swaggerui_blueprint(
    base_url="/swagger-ui",
    api_url="/spec"
)

app.register_blueprint(swagger_ui_bd)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
