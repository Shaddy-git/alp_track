from uuid import uuid4

import pytest
from werkzeug.security import check_password_hash

from extensions import db
from models.user import User


@pytest.fixture
def registered_user(app, client):
    """Создаёт тестового пользователя и удаляет его после теста."""

    unique_id = uuid4().hex[:12]
    username = f"test_{unique_id}"
    password = "TestPassword123!"

    user_data = {
        "username": username,
        "email": f"{username}@example.com",
        "password": password,
        "full_name": "Тестовый альпинист",
        "experience_level": 3,
    }

    response = client.post(
        "/api/auth/register",
        json=user_data,
    )

    assert response.status_code == 201, response.get_json()

    user_id = response.get_json()["user"]["id"]

    try:
        yield {
            "id": user_id,
            "username": username,
            "password": password,
            "data": user_data,
            "response": response,
        }
    finally:
        # Сервис регистрации выполняет commit самостоятельно,
        # поэтому тестовые данные нужно удалять явно.
        with app.app_context():
            db.session.rollback()
            user = db.session.get(User, user_id)
            if user is not None:
                db.session.delete(user)
                db.session.commit()
            db.session.remove()


def test_registration_success(app, registered_user):
    """Пользователь появляется в настоящей PostgreSQL."""
    data = registered_user["response"].get_json()

    assert data["user"]["username"] == registered_user["username"]
    assert data["user"]["role"] == "climber"
    assert data["user"]["experience_level"] == 3
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]

    with app.app_context():
        user = db.session.get(User, registered_user["id"])

        assert user is not None
        assert user.username == registered_user["username"]
        assert user.full_name == "Тестовый альпинист"
        assert user.password_hash != registered_user["password"]
        assert check_password_hash(
            user.password_hash,
            registered_user["password"],
        )


def test_duplicate_username(client, registered_user):
    """Повторная регистрация логина запрещена."""
    duplicate_data = registered_user["data"].copy()
    duplicate_data["email"] = "another@example.com"

    response = client.post(
        "/api/auth/register",
        json=duplicate_data,
    )

    assert response.status_code == 409
    assert "error" in response.get_json()


def test_login_success(client, registered_user):
    """Корректные данные позволяют получить JWT."""
    response = client.post(
        "/api/auth/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data["access_token"], str)
    assert data["access_token"]
    assert data["user"]["username"] == registered_user["username"]


def test_login_wrong_password(client, registered_user):
    """Неверный пароль не позволяет войти."""
    response = client.post(
        "/api/auth/login",
        json={
            "username": registered_user["username"],
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert "error" in response.get_json()


def test_profile_with_token(client, registered_user):
    """JWT позволяет получить профиль текущего пользователя."""
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["access_token"]

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == registered_user["id"]
    assert data["username"] == registered_user["username"]


def test_profile_without_token(client):
    """Защищённый маршрут не работает без JWT."""
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_registration_invalid_experience(client):
    """Уровень подготовки вне диапазона 1–5 запрещён."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": f"invalid_{uuid4().hex[:12]}",
            "email": "invalid@example.com",
            "password": "TestPassword123!",
            "experience_level": 6,
        },
    )

    assert response.status_code == 400
    assert "details" in response.get_json()