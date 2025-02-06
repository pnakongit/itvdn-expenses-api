from flask import blueprints, request, jsonify, Response
from app.db import db, Expenses

bp = blueprints.Blueprint("expenses", __name__, url_prefix="/expenses")


@bp.route("/", methods=["POST"])
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


@bp.route("/", methods=["GET"])
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


@bp.route("/<int:pk>", methods=["GET"])
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


@bp.route("/<int:pk>", methods=["PATCH"])
def update_expense(pk: int) -> (Response, int):
    """
        Update an expense
        You can update an expense by passing its title or amount in
        ---
        tags:
          - expenses
        parameters:
          - in: path
            name: pk
            type: integer
            description: Expense ID
            required: true
          - in: body
            name: Expenses
            description: Expenses title and amount
            required: true
            schema:
              $ref: "#definitions/ExpensePatch"
        responses:
          200:
            description: OK
            schema:
              $ref: "#definitions/ExpenseOut"
        """
    expense = db.get_or_404(Expenses, pk, description="Expense not found")
    expense.title = request.json.get("title", expense.title)
    expense.amount = request.json.get("amount", expense.amount)
    db.session.commit()

    return jsonify({
        "id": expense.id,
        "title": expense.title,
        "amount": expense.amount,
    }), 200


@bp.route("/<int:pk>", methods=["DELETE"])
def delete_expense(pk: int) -> (Response, int):
    """
    Delete an expense
    You can delete an expense by passing its ID to path

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
      204:
        description: Not content
      404:
        schema:
          $ref: "#definitions/NotFound"

    """
    expense = db.get_or_404(Expenses, pk, description="Expense not found")
    db.session.delete(expense)
    db.session.commit()

    return "", 204
