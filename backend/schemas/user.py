from marshmallow import Schema, fields, validate


class UserUpdateSchema(Schema):
    """Схема обновления профиля пользователя.
    """
    
    full_name = fields.Str(validate=validate.Length(max=120))
    email = fields.Email()
    experience_level = fields.Int(validate=validate.Range(min=1, max=5))


class UserRoleSchema(Schema):
    """Схема смены роли пользователя (только для admin)."""
    
    role = fields.Str(
        required=True,
        validate=validate.OneOf(['climber', 'instructor', 'admin'])
    )


class UserResponseSchema(Schema):
    """Схема ответа с данными пользователя.
    
    НЕ включает password_hash  критично для безопасности.
    """
    
    id = fields.Int()
    username = fields.Str()
    email = fields.Email()
    full_name = fields.Str(allow_none=True)
    role = fields.Str()
    experience_level = fields.Int()
    created_at = fields.DateTime()