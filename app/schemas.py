from marshmallow import Schema, fields, validate, validates, ValidationError
from app.db import db, User


class ExpenseSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    amount = fields.Float(required=True, validate=validate.Range(min=0))


class ExpenseOutSchema(ExpenseSchema):
    user_id = fields.Integer(dump_only=True)


expense_schema = ExpenseSchema()
expense_out_schema = ExpenseOutSchema()
expense_update_schema = ExpenseSchema(partial=True)
expenses_schema = ExpenseSchema(many=True)


class UserSchemaLogin(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=4, max=20))
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=4))


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=4, max=20))
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=4))

    @validates("username")
    def validate_username(self, value: str, **kwargs) -> None:
        user = db.session.query(User).filter(User.username == value).first()
        if user is not None:
            raise ValidationError("Username already exists")


user_schema = UserSchema()
user_schema_login = UserSchemaLogin()
