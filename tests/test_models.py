from werkzeug.security import check_password_hash

from app.db import User


class TestUserModel:

    def test_set_password_have_to_set_hash(self) -> None:
        user_password = "test_password"
        user = User(username="username")
        user.set_password(user_password)

        assert check_password_hash(user.password, user_password)

    def test_check_password(self) -> None:
        user_password = "test_password"
        user = User(username="username")
        user.set_password(user_password)

        assert user.check_password(user_password)

    def test_string_representation(self, default_user) -> None:
        assert str(default_user) == f"<User {default_user.id} {default_user.username}>"


class TestExpenseModel:

    def test_string_representation(self, default_expense) -> None:
        assert str(default_expense) == f"<{default_expense.id} - {default_expense.title}>"
