import os
import sys
from pathlib import Path

import pytest
from dotenv import dotenv_values
from sqlalchemy.engine import make_url

# Корневая директория проекта
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Чтобы работали импорты из backend
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))


def get_test_database_url():
    """Читает и проверяет подключение к тестовой БД."""

    settings = dotenv_values(PROJECT_ROOT / ".env.test")
    database_url = (
        os.environ.get("TEST_DATABASE_URL")
        or settings.get("TEST_DATABASE_URL")
    )

    if not database_url:
        raise RuntimeError(
            "Не задан TEST_DATABASE_URL в файле .env.test"
        )

    url = make_url(database_url)

    if (
        url.get_backend_name() != "postgresql"
        or url.database != "alptrack_test"
        or url.host not in ("localhost", "127.0.0.1", "test-db")
    ):
        raise RuntimeError(
            "Тесты разрешено запускать только с локальной "
            "PostgreSQL базой alptrack_test"
        )

    return database_url


@pytest.fixture(scope="session")
def app():
    """Создаёт Flask-приложение с тестовой конфигурацией."""

    # Проверяем адрес до инициализации приложения.
    test_database_url = get_test_database_url()

    from app import create_app
    from config import Config

    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = test_database_url
        JWT_SECRET_KEY = "alptrack-test-jwt-secret-key-2026-only-for-testing"
        SECRET_KEY = "alptrack-test-flask-secret-key-2026-only-for-testing"

    application = create_app(TestConfig)

    yield application

    with application.app_context():
        from extensions import db
        db.session.remove()
        db.engine.dispose()


@pytest.fixture
def client(app):
    """HTTP-клиент Flask для обращения к API без браузера."""
    return app.test_client()