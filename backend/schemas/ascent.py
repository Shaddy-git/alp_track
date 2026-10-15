from marshmallow import Schema, fields, validate


class AscentSchema(Schema):
    """Схема валидации данных о восхождении."""
    
    user_id = fields.Int(required=True)
    mountain_id = fields.Int(required=True)
    group_id = fields.Int(load_default=None)
    ascent_date = fields.Date(required=True)
    is_successful = fields.Bool(load_default=False)
    notes = fields.Str(validate=validate.Length(max=1000), load_default=None)


class AscentUpdateSchema(Schema):
    """Схема обновления восхождения (все поля опциональны)."""
    
    mountain_id = fields.Int()
    group_id = fields.Int()
    ascent_date = fields.Date()
    is_successful = fields.Bool()
    notes = fields.Str(validate=validate.Length(max=1000))