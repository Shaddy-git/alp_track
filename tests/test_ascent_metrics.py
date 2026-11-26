import uuid

import pytest
from flask_jwt_extended import create_access_token


@pytest.fixture
def ascent_setup(app):
    """Создаёт тестовые объекты и удаляет их после теста."""
    from extensions import db
    from models.ascent import Ascent
    from models.mountain import Mountain
    from models.user import User

    suffix = uuid.uuid4().hex[:12]

    with app.app_context():
        admin = User(
            username=f"admin_{suffix}",
            email=f"admin_{suffix}@example.test",
            password_hash="test-only",
            role="admin",
            experience_level=5,
        )
        climber = User(
            username=f"climber_{suffix}",
            email=f"climber_{suffix}@example.test",
            password_hash="test-only",
            role="climber",
            experience_level=5,
        )
        mountain = Mountain(
            name=f"Test Mountain {suffix}",
            height=2500,
            country="Testland",
            difficulty_level=2,
        )

        db.session.add_all([admin, climber, mountain])
        db.session.commit()

        admin_id = admin.id
        climber_id = climber.id
        mountain_id = mountain.id

        admin_token = create_access_token(identity=str(admin_id))
        climber_token = create_access_token(identity=str(climber_id))

    yield {
        "climber_id": climber_id,
        "mountain_id": mountain_id,
        "admin_headers": {
            "Authorization": f"Bearer {admin_token}"
        },
        "climber_headers": {
            "Authorization": f"Bearer {climber_token}"
        },
    }

    with app.app_context():
        db.session.rollback()

        Ascent.query.filter_by(user_id=climber_id).delete()

        db.session.query(Mountain).filter_by(
            id=mountain_id
        ).delete()

        db.session.query(User).filter(
            User.id.in_([admin_id, climber_id])
        ).delete(synchronize_session=False)

        db.session.commit()


def ascent_payload(setup):
    return {
        "user_id": setup["climber_id"],
        "mountain_id": setup["mountain_id"],
        "ascent_date": "2026-11-26",
        "is_successful": True,
    }


def test_create_read_update_ascent_metrics(client, ascent_setup):
    """Новые поля сохраняются, читаются и обновляются."""
    data = ascent_payload(ascent_setup)
    data.update({
        "duration_minutes": 360,
        "elevation_gain_m": 1200,
        "effort_rating": 4,
    })

    headers = ascent_setup["admin_headers"]

    response = client.post(
        "/api/ascents",
        json=data,
        headers=headers,
    )
    assert response.status_code == 201, response.get_json()

    created = response.get_json()["ascent"]
    ascent_id = created["id"]

    assert created["duration_minutes"] == 360
    assert created["elevation_gain_m"] == 1200
    assert created["effort_rating"] == 4

    response = client.get(
        f"/api/ascents/{ascent_id}",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.get_json()["effort_rating"] == 4

    response = client.put(
        f"/api/ascents/{ascent_id}",
        headers=headers,
        json={
            "duration_minutes": 420,
            "elevation_gain_m": 1500,
            "effort_rating": 5,
        },
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/ascents/{ascent_id}",
        headers=headers,
    )
    assert response.status_code == 200

    updated = response.get_json()
    assert updated["duration_minutes"] == 420
    assert updated["elevation_gain_m"] == 1500
    assert updated["effort_rating"] == 5

    response = client.get(
        "/api/ascents/my",
        headers=ascent_setup["climber_headers"],
    )
    assert response.status_code == 200
    assert any(
        item["id"] == ascent_id
        and item["effort_rating"] == 5
        for item in response.get_json()
    )
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("duration_minutes", 0),
        ("duration_minutes", -10),
        ("elevation_gain_m", -1),
        ("effort_rating", 0),
        ("effort_rating", 6),
        ("effort_rating", "invalid"),
    ],
)
def test_invalid_metrics_return_400(
    client, ascent_setup, field, value
):
    """Некорректные показатели отклоняются API."""
    data = ascent_payload(ascent_setup)
    data[field] = value

    response = client.post(
        "/api/ascents",
        json=data,
        headers=ascent_setup["admin_headers"],
    )

    assert response.status_code == 400
    assert field in response.get_json()["details"]


def test_old_ascent_format_still_works(client, ascent_setup):
    """Старые запросы без новых полей остаются допустимыми."""
    response = client.post(
        "/api/ascents",
        json=ascent_payload(ascent_setup),
        headers=ascent_setup["admin_headers"],
    )

    assert response.status_code == 201, response.get_json()

    created = response.get_json()["ascent"]
    assert created["duration_minutes"] is None
    assert created["elevation_gain_m"] is None
    assert created["effort_rating"] is None