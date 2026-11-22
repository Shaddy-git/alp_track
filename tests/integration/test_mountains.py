from uuid import uuid4

import pytest

from extensions import db
from models.user import User
from models.mountain import Mountain


@pytest.fixture
def auth_users(app, client):
    """Создаёт администратора и альпиниста для теста."""
    created_ids = []
    accounts = {}

    try:
        for role in ("admin", "climber"):
            username = f"mountain_{role}_{uuid4().hex[:10]}"
            password = "TestPassword123!"

            response = client.post(
                "/api/auth/register",
                json={
                    "username": username,
                    "email": f"{username}@example.com",
                    "password": password,
                    "experience_level": 3,
                },
            )
            assert response.status_code == 201, response.get_json()

            user_id = response.get_json()["user"]["id"]
            created_ids.append(user_id)

            if role == "admin":
                with app.app_context():
                    user = db.session.get(User, user_id)
                    user.role = "admin"
                    db.session.commit()

            response = client.post(
                "/api/auth/login",
                json={"username": username, "password": password},
            )
            assert response.status_code == 200

            token = response.get_json()["access_token"]

            accounts[role] = {
                "id": user_id,
                "headers": {"Authorization": f"Bearer {token}"},
            }

        yield accounts

    finally:
        with app.app_context():
            db.session.rollback()
            for user_id in created_ids:
                user = db.session.get(User, user_id)
                if user is not None:
                    db.session.delete(user)
            db.session.commit()
            db.session.remove()


@pytest.fixture
def mountain_data(app, auth_users):
    """Уникальные данные горы с очисткой после теста."""
    data = {
        "name": f"TestMountain_{uuid4().hex}",
        "height": 5642,
        "country": "Россия",
        "difficulty_level": 3,
    }

    yield data

    with app.app_context():
        db.session.rollback()
        mountain = Mountain.query.filter_by(
            name=data["name"]
        ).first()

        if mountain is not None:
            db.session.delete(mountain)
            db.session.commit()

        db.session.remove()


def test_admin_can_create_mountain(client, auth_users, mountain_data):
    """Администратор может создать гору."""
    response = client.post(
        "/api/mountains",
        json=mountain_data,
        headers=auth_users["admin"]["headers"],
    )

    assert response.status_code == 201
    assert response.get_json()["mountain"]["name"] == mountain_data["name"]


def test_climber_cannot_create_mountain(client, auth_users, mountain_data):
    """Обычному альпинисту создание запрещено."""
    response = client.post(
        "/api/mountains",
        json=mountain_data,
        headers=auth_users["climber"]["headers"],
    )

    assert response.status_code == 403


def test_create_mountain_without_token(client, mountain_data):
    """Без JWT создание горы запрещено."""
    response = client.post("/api/mountains", json=mountain_data)

    assert response.status_code == 401


def test_duplicate_mountain(client, auth_users, mountain_data):
    """Нельзя добавить две горы с одинаковым названием."""
    headers = auth_users["admin"]["headers"]

    first = client.post(
        "/api/mountains", json=mountain_data, headers=headers
    )
    second = client.post(
        "/api/mountains", json=mountain_data, headers=headers
    )

    assert first.status_code == 201
    assert second.status_code == 409
    
@pytest.mark.parametrize(
    "field,value",
    [
        ("height", 0),
        ("height", 9001),
        ("difficulty_level", 0),
        ("difficulty_level", 6),
    ],
)
def test_invalid_mountain_data(
    client, auth_users, mountain_data, field, value
):
    """Недопустимые значения отклоняются."""
    payload = mountain_data.copy()
    payload[field] = value

    response = client.post(
        "/api/mountains",
        json=payload,
        headers=auth_users["admin"]["headers"],
    )

    assert response.status_code == 400
    assert "details" in response.get_json()