from flask import Flask, request, jsonify
from flask.wrappers import Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column

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
def index() -> (dict, 200):
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
def get_expenses() -> (Response, 200):
    pass


@app.route("/expenses/<int:pk>", methods=["GET"])
def get_expense(pk: int) -> (Response, 200):
    pass


@app.route("/expenses/<int:pk>", methods=["PATCH"])
def update_expense() -> (Response, 200):
    pass


@app.route("/expenses/<int:pk>", methods=["DELETE"])
def delete_expense() -> (Response, 200):
    pass


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
