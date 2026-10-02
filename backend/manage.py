# backend/manage.py
from app import create_app
from extensions import db

# Создаём приложение для CLI (flask db migrate / upgrade)
app = create_app()

# Регистрируем модели в контексте приложения
with app.app_context():
    from models import user, mountain, group, ascent  # noqa: F401

if __name__ == '__main__':
    app.run()