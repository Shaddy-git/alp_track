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

class GroupUpdateSchema(Schema):
    """Схема обновления группы (все поля опциональны)."""
    
    name = fields.Str(validate=validate.Length(min=1, max=120))
    start_date = fields.Date()
    end_date = fields.Date()
    status = fields.Str(
        validate=validate.OneOf(['planning', 'active', 'completed', 'cancelled'])
    )


class JoinGroupSchema(Schema):
    """Схема для самостоятельного присоединения к группе.
    
    Пользователь сам себя добавляет - user_id берётся из JWT.
    """
    pass