from flask import Flask
from flask_sqlalchemy import SQLAlchemy

DATABASE_URI = "sqlite:///expenses.sqlite3"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


@app.route('/')
def index() -> (dict, 200):
    return {"message": "Hello from Expenses API!"}, 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
