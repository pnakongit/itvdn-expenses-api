import pytest
from marshmallow import ValidationError

from app.db import User
from app.schemas import UserSchema


class TestUserSchema:

    def test_validate_valid_data(self, user_schema, ) -> None:
        data = {
            "username": "unique_user_name",
            "password": "password",
        }
        result = user_schema.load(data)

        assert result == data

    def test_validate_username_already_exists(self, user_schema, default_user: User) -> None:
        schema = UserSchema()
        data = {
            "username": default_user.username,
            "password": "password",
        }

        expected_message = {"username": ["Username already exists"]}

        with pytest.raises(ValidationError) as e:
            schema.load(data)

        assert e.value.messages == expected_message
