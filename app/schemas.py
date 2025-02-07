from marshmallow import Schema, fields, validate


class ExpenseSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    amount = fields.Float(required=True, validate=validate.Range(min=0))


expense_schema = ExpenseSchema()
expense_update_schema = ExpenseSchema(partial=True)
expenses_schema = ExpenseSchema(many=True)
