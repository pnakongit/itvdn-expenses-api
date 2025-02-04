from flask import Flask, request, jsonify
from flask.wrappers import Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

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
    return {"message": "Hello from Expenses API!"}, 200


@app.route("/expenses", methods=["POST"])
def create_expense() -> (Response, 201):
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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
