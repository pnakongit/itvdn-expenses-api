import os
import pytest

from flask import Flask, url_for
from flask_jwt_extended import create_access_token, create_refresh_token

from app import create_app
from app.db import db, User, Expenses
from app.schemas import UserSchema


@pytest.fixture(scope="module")
def test_client() -> Flask.test_client:
    os.environ["CONFIG_TYPE"] = "app.config.TestingConfig"
    flask_app = create_app()

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client


@pytest.fixture(scope="module")
def init_database(test_client) -> None:
    db.create_all()
    yield
    db.drop_all()


@pytest.fixture
def default_user(init_database) -> User:
    user = User(username="test_username")
    user.set_password("test_password")

    db.session.add(user)
    db.session.commit()

    return user


@pytest.fixture
def default_expense(default_user) -> Expenses:
    expense = Expenses(title="Test title", amount=100)
    expense.user_id = default_user.id

    db.session.add(expense)
    db.session.commit()

    return expense


@pytest.fixture(autouse=True)
def clear_db(init_database) -> None:
    yield
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
    db.session.close()


@pytest.fixture
def user_schema() -> UserSchema:
    return UserSchema()


@pytest.fixture
def default_user_access_token(default_user) -> str:
    return create_access_token(identity=default_user.id)


@pytest.fixture
def default_user_refresh_token(default_user: User) -> str:
    return create_refresh_token(identity=default_user.id)


@pytest.fixture
def registration_url() -> str:
    return url_for("auth.register")


@pytest.fixture
def login_url() -> str:
    return url_for("auth.login")

@pytest.fixture
def refresh_token_url() -> str:
    return url_for("auth.refresh")
