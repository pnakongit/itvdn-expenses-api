from flask import blueprints, request, jsonify, Response
from flask_jwt_extended import jwt_required, current_user
from werkzeug.exceptions import Forbidden

from app.db import db, Expenses
from app.schemas import (
    expense_schema,
    expense_out_schema,
    expense_update_schema, expenses_out_schema,
)

bp = blueprints.Blueprint("expenses", __name__, url_prefix="/expenses")


@bp.route("/", methods=["POST"])
@jwt_required()
def create_expense() -> (Response, 201):
    """
    Create a new expense
    You can create a new expense by passing its title and amount in

    ---
    security:
      - BearerAuth: []
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

    data = expense_schema.load(request.json)

    expense = Expenses(
        user_id=current_user.id,
        **expense_schema.load(data)
    )

    db.session.add(expense)
    db.session.commit()

    return jsonify(
        expense_out_schema.dump(expense)
    ), 201


@bp.route("/", methods=["GET"])
@jwt_required()
def get_expenses() -> (Response, int):
    """
    Get all expenses
    Return a list of all expenses

    ---
    security:
      - BearerAuth: []
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

    data = expenses_out_schema.dump(current_user.expenses)
    return jsonify(data), 200


@bp.route("/<int:pk>", methods=["GET"])
@jwt_required()
def get_expense(pk: int) -> (Response, int):
    """
    Get an expense
    Return a single expense

    ---
    security:
      - BearerAuth: []
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

    if expense.user_id != current_user.id:
        raise Forbidden(
            description="You are not authorized to view this expense"
        )
    data = expense_out_schema.dump(expense)
    return jsonify(data), 200


@bp.route("/<int:pk>", methods=["PATCH"])
@jwt_required()
def update_expense(pk: int) -> (Response, int):
    """
        Update an expense
        You can update an expense by passing its title or amount in

        ---
        security:
          - BearerAuth: []
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

    if expense.user_id != current_user.id:
        raise Forbidden(
            description="You are not authorized to patch this expense"
        )

    data = expense_update_schema.load(request.json)
    expense.title = data.get("title", expense.title)
    expense.amount = data.get("amount", expense.amount)
    db.session.commit()

    return jsonify(expense_out_schema.dump(expense)), 200


@bp.route("/<int:pk>", methods=["DELETE"])
@jwt_required()
def delete_expense(pk: int) -> (Response, int):
    """
    Delete an expense
    You can delete an expense by passing its ID to path

    ---
    security:
      - BearerAuth: []
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
    if expense.user_id != current_user.id:
        raise Forbidden(
            description="You are not authorized to delete this expense"
        )
    db.session.delete(expense)
    db.session.commit()

    return "", 204
