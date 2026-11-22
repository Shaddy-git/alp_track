from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from services import ascent_service

@pytest.fixture
def ascent_data(monkeypatch):
    """Подмена модели и сессии БД"""
    user = SimpleNamespace(
        id = 1,
        username = "test_climber",
        experience_level = 3,
    )
    mountain = SimpleNamespace(
        id = 2,
        name = "Эльбрус",
        difficulty_level = 3,
    )

    user_model = SimpleNamespace(
        query = SimpleNamespace(get=Mock(return_value=user))
    )
    mountain_model = SimpleNamespace(
        query = SimpleNamespace(get=Mock(return_value=mountain))
    )

    # Модель ascent подменяем с помощью Mock: он имитирует поиск и создание записи
    ascent_model = Mock()
    ascent_model.query.filter_by.return_value.first.return_value = None
    ascent_model.side_effect = (
        lambda **kwargs: SimpleNamespace(**kwargs)
    )

    session = Mock()
    fake_db = SimpleNamespace(session=session)

    monkeypatch.setattr(ascent_service, "User", user_model)
    monkeypatch.setattr(ascent_service, "Mountain", mountain_model)
    monkeypatch.setattr(ascent_service, "Ascent", ascent_model)
    monkeypatch.setattr(ascent_service, "db", fake_db)

    monkeypatch.setattr(
        ascent_service,
        "validate_ascent_dates",
        Mock(return_value=(True, "")),
    )

    return SimpleNamespace(
        user=user,
        mountain=mountain,
        ascent_model=ascent_model,
        session=session,
    )

def create_test_ascent():
    return ascent_service.create_ascent(
        user_id=1,
        mountain_id=2,
        group_id=None,
        ascent_date=date(2026, 7, 15),
    )

def test_create_ascent_succes(ascent_data):
    """Корректное восхождение создается и сохраняется"""
    succes, message, ascent = create_test_ascent()

    assert succes is True
    assert message == "Восхождение создано"
    assert ascent is not None

    assert ascent.user_id == 1
    assert ascent.mountain_id == 2
    assert ascent.ascent_date == date(2026, 7, 15)

    ascent_data.session.add.assert_called_once_with(ascent)
    ascent_data.session.commit.assert_called_once()

def test_create_ascent_user_not_found(ascent_data):
    """Нельзя создать восхождение без пользователя."""
    ascent_service.User.query.get.return_value = None

    success, message, ascent = create_test_ascent()

    assert success is False
    assert message == "Пользователь не найден"
    assert ascent is None
    ascent_data.session.commit.assert_not_called()


def test_create_ascent_mountain_not_found(ascent_data):
    """Нельзя создать восхождение на несуществующую гору."""
    ascent_service.Mountain.query.get.return_value = None

    success, message, ascent = create_test_ascent()

    assert success is False
    assert message == "Гора не найдена"
    assert ascent is None
    ascent_data.session.commit.assert_not_called()


def test_create_ascent_insufficient_experience(ascent_data):
    """Недостаточный опыт запрещает восхождение."""
    ascent_data.user.experience_level = 2

    success, message, ascent = create_test_ascent()

    assert success is False
    assert "Недостаточный уровень подготовки" in message
    assert ascent is None
    ascent_data.session.commit.assert_not_called()


def test_create_ascent_equal_experience(ascent_data):
    """Уровень подготовки, равный сложности горы, допустим."""
    ascent_data.user.experience_level = 3

    success, _, ascent = create_test_ascent()

    assert success is True
    assert ascent is not None
    ascent_data.session.commit.assert_called_once()


def test_create_ascent_invalid_date(ascent_data, monkeypatch):
    """При недопустимой дате запись не создаётся."""
    monkeypatch.setattr(
        ascent_service,
        "validate_ascent_dates",
        Mock(return_value=(False, "Дата вне периода группы")),
    )

    success, message, ascent = create_test_ascent()

    assert success is False
    assert message == "Дата вне периода группы"
    assert ascent is None
    ascent_data.session.commit.assert_not_called()


def test_create_ascent_duplicate(ascent_data):
    """Нельзя дважды записать одно восхождение."""
    existing = SimpleNamespace(id=42)

    ascent_data.ascent_model.query.filter_by.return_value.first.return_value = (
        existing
    )

    success, message, ascent = create_test_ascent()

    assert success is False
    assert "уже зафиксировано" in message
    assert ascent is None
    ascent_data.session.commit.assert_not_called()


def test_create_ascent_duplicate_search_fields(ascent_data):
    """Дубликат ищется по пользователю, горе и дате."""
    create_test_ascent()

    ascent_data.ascent_model.query.filter_by.assert_called_once_with(
        user_id=1,
        mountain_id=2,
        ascent_date=date(2026, 7, 15),
    )


def test_create_ascent_saves_notes_and_result(ascent_data):
    """Сохраняются результат восхождения и примечание."""
    success, _, ascent = ascent_service.create_ascent(
        user_id=1,
        mountain_id=2,
        group_id=None,
        ascent_date=date(2026, 7, 15),
        is_successful=True,
        notes="Вершина достигнута",
    )

    assert success is True
    assert ascent.is_successful is True
    assert ascent.notes == "Вершина достигнута"
    ascent_data.session.commit.assert_called_once()





