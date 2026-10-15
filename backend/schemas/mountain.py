from marshmallow import Schema, fields, validate


class MountainSchema(Schema):
    """Схема валидации данных о горе."""
    
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=120)
    )
    height = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=9000)
    )
    country = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=80)
    )
    difficulty_level = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=5)
    )