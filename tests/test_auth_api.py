from flask import url_for

from app.db import db, User
from app.schemas import UserSchema

user_schema = UserSchema()


class TestRegister:

    def test_register_with_valid_data(
            self,
            test_client,
            registration_url
    ) -> None:
        payload = {
            "username": "test_username",
            "password": "my_super_password",
        }
        response = test_client.post(registration_url, json=payload)

        created_user = (
            db.session.query(User)
            .filter_by(username=payload["username"])
            .first()
        )

        assert response.status_code == 201
        assert response.json == user_schema.dump(created_user)

    def test_register_with_invalid_data(
            self,
            test_client,
            registration_url
    ) -> None:
        registration_url = url_for("auth.register")
        payload = {
            "username": "123",
            "password": "123",
        }
        response = test_client.post(registration_url, json=payload)

        assert response.status_code == 400


class TestLogin:
    def test_login_with_valid_data(
            self,
            test_client,
            default_user,
            login_url
    ) -> None:
        login_url = url_for("auth.login")
        payload = {
            "username": default_user.username,
            "password": "test_password",
        }
        response = test_client.post(login_url, json=payload)
        assert response.status_code == 201
        assert "access_token" in response.json
        assert "refresh_token" in response.json

    def test_login_with_invalid_data(
            self,
            test_client,
            login_url
    ) -> None:
        payload = {
            "username": "some_username",
            "password": "some_password",
        }
        response = test_client.post(login_url, json=payload)
        expected_error = {
            "code": 401,
            "name": "Unauthorized",
            "description": "Incorrect credentials",
        }
        assert response.status_code == 401
        assert "error" in response.json
        assert response.json["error"] == expected_error


class TestRefreshToken:

    def test_refresh_token(
            self,
            test_client,
            refresh_token_url,
            default_user_refresh_token
    ) -> None:
        response = test_client.post(
            refresh_token_url,
            headers={"Authorization": "Bearer " + default_user_refresh_token},
        )

        assert response.status_code == 200
        assert "access_token" in response.json

    def test_can_not_refresh_with_access_token(
            self,
            test_client,
            refresh_token_url,
            default_user_access_token
    ) -> None:
        response = test_client.post(
            refresh_token_url,
            headers={"Authorization": "Bearer " + default_user_access_token},
        )
        expected_error = {'msg': 'Only refresh tokens are allowed'}

        assert response.status_code == 422
        assert response.json == expected_error
