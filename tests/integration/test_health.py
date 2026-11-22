from sqlalchemy import text
from extensions import db

def test_health_endpoint(client):
    """Проверка доступности API и подключение к PostgreSQL"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()

    assert data["status"] == "ok"
    assert data["database"] == "connected"

def test_database_is_test_database(app):
    """Проверяет, что приложение подключено к нужной БД"""
    with app.app_context():
        database_name = db.session.execute(
            text("SELECT current_database()")
        ).scalar_one()

    assert database_name == "alptrack_test"