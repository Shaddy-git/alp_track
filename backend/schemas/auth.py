# backend/schemas/auth.py
from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    """Схема валидации регистрации нового пользователя."""
    
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=80)
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128),
        load_only=True  # никогда не возвращаем пароль в ответе
    )
    experience_level = fields.Int(
        validate=validate.Range(min=1, max=5),
        load_default=1
    )


class LoginSchema(Schema):
    """Схема валидации входа."""
    
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)