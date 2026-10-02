# backend/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy 2.x."""
    pass


# Создаём экземпляры расширений БЕЗ привязки к app.
# Это делается, чтобы избежать циклических импортов.
db = SQLAlchemy(model_class=Base)
migrate = Migrate()
jwt = JWTManager()