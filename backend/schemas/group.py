# backend/schemas/group.py
from marshmallow import Schema, fields, validate


class GroupSchema(Schema):
    """Схема группы."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    leader_id = fields.Int(required=True)
    status = fields.Str(
        validate=validate.OneOf(['planning', 'active', 'completed', 'cancelled']),
        load_default='planning'
    )


class AddMemberSchema(Schema):
    """Схема для добавления участника в группу."""
    user_id = fields.Int(required=True)