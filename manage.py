# manage.py - точка входа для Flask CLI
import os
import sys

# Добавляем папку backend в sys.path, чтобы импорты работали
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app  # noqa: E402
from extensions import db   # noqa: E402

app = create_app()

# Регистрируем модели, чтобы Flask-Migrate их видел
with app.app_context():
    from models import user, mountain, group, ascent  # noqa: F401, E402

if __name__ == '__main__':
    app.run(debug=True, port=5000)