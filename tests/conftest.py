import os
import pytest

from flask import Flask

from app import create_app


@pytest.fixture(scope="module")
def test_client() -> Flask.test_client:
    os.environ["CONFIG_TYPE"] = "app.config.TestingConfig"
    flask_app = create_app()

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client
