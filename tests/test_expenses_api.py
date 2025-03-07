import pytest

from flask import url_for

from app.db import db, Expenses, User
from app.schemas import expense_out_schema, expenses_out_schema

GET_EXPENSE_VIEW_NAME = "expenses.get_expense"
UPDATE_EXPENSE_VIEW_NAME = "expenses.update_expense"
DELETE_EXPENSE_VIEW_NAME = "expenses.delete_expense"


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


class TestGetExpense:
    def test_auth_required(
            self,
            test_client,
            headers_with_access_token,
            default_expense
    ) -> None:
        expense_url = url_for("expenses.get_expense", pk=default_expense.id)
        response = test_client.get(expense_url)
        assert response.status_code == 401

        response = test_client.get(expense_url, headers=headers_with_access_token)
        assert response.status_code == 200

    def test_return_expense(
            self,
            test_client,
            headers_with_access_token,
            default_expense
    ) -> None:
        expense_url = url_for(GET_EXPENSE_VIEW_NAME, pk=default_expense.id)
        response = test_client.get(expense_url, headers=headers_with_access_token)

        expected_expense = expense_out_schema.dump(default_expense)

        assert response.status_code == 200
        assert response.json == expected_expense

    def test_user_have_access_only_to_own_expenses(
            self,
            test_client,
            headers_with_access_token,
            default_user
    ) -> None:
        another_user = User(
            username="another_user",
        )
        another_user.set_password("test_password")
        db.session.add(another_user)

        expense = expense_sample(user=another_user)
        db.session.add(expense)

        db.session.commit()

        expense_url = url_for(GET_EXPENSE_VIEW_NAME, pk=expense.id)
        response = test_client.get(expense_url, headers=headers_with_access_token)

        assert expense.user != default_user
        assert response.status_code == 403


class TestUpdateExpense:
    def test_auth_required(
            self,
            test_client,
            headers_with_access_token,
            default_expense
    ) -> None:
        pay_load = {
            "title": "New Test Expense",
            "amount": 100,
        }
        update_expense_url = url_for(UPDATE_EXPENSE_VIEW_NAME, pk=default_expense.id)
        response = test_client.patch(update_expense_url, json=pay_load)
        assert response.status_code == 401

        response = test_client.patch(update_expense_url, json=pay_load, headers=headers_with_access_token)
        assert response.status_code == 200

    def test_user_can_update_only_to_own_expenses(
            self,
            test_client,
            headers_with_access_token,
            default_user
    ) -> None:
        payload = {
            "title": "New Test Expense",
            "amount": 100,
        }
        another_user = User(
            username="another_user",
        )
        another_user.set_password("test_password")
        db.session.add(another_user)

        expense = expense_sample(user=another_user)
        db.session.add(expense)

        db.session.commit()

        expense_update_url = url_for(UPDATE_EXPENSE_VIEW_NAME, pk=expense.id)
        response = test_client.patch(
            expense_update_url,
            json=payload,
            headers=headers_with_access_token
        )

        assert expense.user != default_user
        assert response.status_code == 403

    def test_update_with_valid_data(
            self,
            test_client,
            headers_with_access_token,
            default_expense
    ) -> None:
        pay_load = {
            "title": default_expense.title + "updated",
            "amount": default_expense.amount + 10,
        }

        update_expense_url = url_for(UPDATE_EXPENSE_VIEW_NAME, pk=default_expense.id)
        response = test_client.patch(
            update_expense_url,
            json=pay_load,
            headers=headers_with_access_token
        )

        expected_expense_data = expense_out_schema.dump(default_expense)

        for field in pay_load:
            assert getattr(default_expense, field) == pay_load[field]

        assert response.status_code == 200
        assert response.json == expected_expense_data

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
    def test_update_with_invalid_field(
            self,
            test_client,
            headers_with_access_token,
            default_expense,
            field_name,
            field_value,
            error_message
    ) -> None:
        pay_load = {field_name: field_value}

        update_expense_url = url_for(UPDATE_EXPENSE_VIEW_NAME, pk=default_expense.id)
        response = test_client.patch(
            update_expense_url,
            json=pay_load,
            headers=headers_with_access_token
        )

        assert response.status_code == 400
        assert error_message == response.json["errors"][field_name][0]


class TestDeleteExpense:
    def test_auth_required(
            self,
            test_client,
            headers_with_access_token,
            default_expense
    ) -> None:
        delete_expense_url = url_for(DELETE_EXPENSE_VIEW_NAME, pk=default_expense.id)
        response = test_client.delete(delete_expense_url)
        assert response.status_code == 401

        response = test_client.delete(delete_expense_url, headers=headers_with_access_token)
        assert response.status_code == 204

    def test_user_can_delete_only_own_expenses(
            self,
            test_client,
            headers_with_access_token,
            default_user
    ) -> None:
        another_user = User(
            username="another_user",
        )
        another_user.set_password("test_password")
        db.session.add(another_user)

        expense = expense_sample(user=another_user)
        db.session.add(expense)

        db.session.commit()

        expense_delete_url = url_for(DELETE_EXPENSE_VIEW_NAME, pk=expense.id)
        response = test_client.patch(
            expense_delete_url,
            headers=headers_with_access_token
        )

        assert expense.user != default_user
        assert response.status_code == 403

    def test_delete_expense(
            self,
            test_client,
            headers_with_access_token,
            default_expense
    ) -> None:
        delete_url = url_for(DELETE_EXPENSE_VIEW_NAME, pk=default_expense.id)
        response = test_client.delete(delete_url, headers=headers_with_access_token)

        assert db.session.get(Expenses, default_expense.id) is None
        assert response.status_code == 204
        assert response.json is None
