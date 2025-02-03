from flask import Flask

app = Flask(__name__)


@app.route('/')
def index() -> (dict, 200):
    return {"message": "Hello from Expenses API!"}, 200


if __name__ == "__main__":
    app.run(debug=True)
