import pytest

from app.db import db, Expenses, User
from app.schemas import expense_out_schema, expenses_out_schema


def expense_sample(*, user: User, **kwargs) -> Expenses:
    title = kwargs.get("title", "test_title")
    amount = kwargs.get("amount", 1)

    return Expenses(user=user, title=title, amount=amount)


class TestExpenseCreate:

    def test_auth_required(
            self,
            test_client,
            headers_with_access_token,
            create_expense_url
    ) -> None:
        pay_load = {
            "title": "Test Expense",
            "amount": 100,
        }

        response = test_client.post(create_expense_url, json=pay_load)
        assert response.status_code == 401

        response = test_client.post(create_expense_url, json=pay_load, headers=headers_with_access_token)
        assert response.status_code == 201

    def test_create_with_valid_data(
            self,
            test_client,
            headers_with_access_token,
            create_expense_url
    ) -> None:
        pay_load = {
            "title": "Test Expense",
            "amount": 100,
        }

        response = test_client.post(create_expense_url, json=pay_load, headers=headers_with_access_token)
        created_expense = db.session.query(Expenses).filter(Expenses.id == response.json['id']).first()
        expected_response = expense_out_schema.dump(created_expense)

        assert response.status_code == 201
        assert response.json == expected_response

    @pytest.mark.parametrize(
        "field_name, field_value, error_message",
        [
            ("title", "", "Length must be between 1 and 50."),
            ("title", "t" * 51, "Length must be between 1 and 50."),
            ("title", 1, "Not a valid string."),
            ("amount", -1, "Must be greater than or equal to 0."),
            ("amount", "str", "Not a valid number."),
        ]
    )
    def test_create_with_invalid_field(
            self,
            test_client,
            headers_with_access_token,
            create_expense_url,
            field_name,
            field_value,
            error_message
    ) -> None:
        pay_load = {
            "title": field_value if field_name == "title" else "Test Expense",
            "amount": field_value if field_name == "amount" else 1,
        }

        response = test_client.post(create_expense_url, json=pay_load, headers=headers_with_access_token)

        assert response.status_code == 400
        assert error_message == response.json["errors"][field_name][0]


class TestGetExpenses:
    def test_auth_required(
            self,
            test_client,
            headers_with_access_token,
            expenses_url
    ) -> None:
        response = test_client.get(expenses_url)
        assert response.status_code == 401

        response = test_client.get(expenses_url, headers=headers_with_access_token)
        assert response.status_code == 200

    def test_should_return_all_users_expenses(
            self,
            test_client,
            headers_with_access_token,
            expenses_url,
            default_user
    ) -> None:
        for _ in range(3):
            db.session.add(expense_sample(user=default_user))

        another_user = User(
            username="another_user",
        )
        another_user.set_password("test_password")
        db.session.add(another_user)

        for _ in range(3):
            db.session.add(expense_sample(user=another_user))

        db.session.commit()

        expected_expenses = expenses_out_schema.dump(default_user.expenses)
        response = test_client.get(expenses_url, headers=headers_with_access_token)

        assert response.status_code == 200
        assert response.json == expected_expenses
