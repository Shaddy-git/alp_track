from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from services import ascent_service


@pytest.fixture
def group_data(monkeypatch):
    """Подготавливает пользователя, группу и восхождения без БД."""

    user = SimpleNamespace(
        id=1,
        experience_level=3,
    )

    group = SimpleNamespace(
        id=10,
        status="planning",
        members=[],
    )

    # У группы две горы: сложность 2 и 3.
    ascents = [
        SimpleNamespace(
            mountain=SimpleNamespace(difficulty_level=2)
        ),
        SimpleNamespace(
            mountain=SimpleNamespace(difficulty_level=3)
        ),
    ]

    user_query = SimpleNamespace(
        get=Mock(return_value=user)
    )
    group_query = SimpleNamespace(
        get=Mock(return_value=group)
    )
    ascent_query = SimpleNamespace(
        filter_by=Mock(
            return_value=SimpleNamespace(
                all=Mock(return_value=ascents)
            )
        )
    )

    monkeypatch.setattr(
        ascent_service, "User",
        SimpleNamespace(query=user_query)
    )
    monkeypatch.setattr(
        ascent_service, "Group",
        SimpleNamespace(query=group_query)
    )
    monkeypatch.setattr(
        ascent_service, "Ascent",
        SimpleNamespace(query=ascent_query)
    )

    return user, group, ascents


def test_join_group_success(group_data):
    """Подготовленный альпинист может вступить в группу."""
    result, reason = ascent_service.can_climber_join_group(1, 10)

    assert result is True
    assert reason == ""


def test_user_not_found(group_data):
    """Несуществующий пользователь получает отказ."""
    ascent_service.User.query.get.return_value = None

    result, reason = ascent_service.can_climber_join_group(999, 10)

    assert result is False
    assert reason == "Пользователь не найден"


def test_group_not_found(group_data):
    """Несуществующая группа получает отказ."""
    ascent_service.Group.query.get.return_value = None

    result, reason = ascent_service.can_climber_join_group(1, 999)

    assert result is False
    assert reason == "Группа не найдена"


def test_user_already_in_group(group_data):
    """Нельзя повторно вступить в одну группу."""
    user, group, _ = group_data
    group.members.append(user)

    result, reason = ascent_service.can_climber_join_group(1, 10)

    assert result is False
    assert "уже состоит" in reason


@pytest.mark.parametrize("status", ["completed", "cancelled"])
def test_join_closed_group(group_data, status):
    """В завершённую или отменённую группу вступать нельзя."""
    _, group, _ = group_data
    group.status = status

    result, reason = ascent_service.can_climber_join_group(1, 10)

    assert result is False
    assert "Нельзя присоединиться" in reason


def test_join_active_group(group_data):
    """В активную группу вступать разрешено."""
    _, group, _ = group_data
    group.status = "active"

    result, reason = ascent_service.can_climber_join_group(1, 10)

    assert result is True
    assert reason == ""


def test_group_without_ascents(group_data):
    """Группа без восхождений не принимает участников."""
    ascent_service.Ascent.query.filter_by.return_value.all.return_value = []

    result, reason = ascent_service.can_climber_join_group(1, 10)

    assert result is False
    assert "нет запланированных восхождений" in reason


def test_insufficient_experience(group_data):
    """Уровень подготовки ниже сложности горы."""
    user, _, _ = group_data
    user.experience_level = 2

    result, reason = ascent_service.can_climber_join_group(1, 10)

    assert result is False
    assert "Недостаточный уровень подготовки" in reason


def test_experience_equals_difficulty(group_data):
    """Подготовка, равная сложности горы, достаточна."""
    user, _, _ = group_data
    user.experience_level = 3

    result, reason = ascent_service.can_climber_join_group(1, 10)

    assert result is True
    assert reason == ""

def test_experience_above_difficulty(group_data):
    """Подготовка выше сложности горы допускается."""
    user, _, _ = group_data
    user.experience_level = 4

    result, reason = ascent_service.can_climber_join_group(1, 10)

    assert result is True
    assert reason == ""


def test_uses_maximum_mountain_difficulty(group_data):
    """Учитывается самая сложная гора, а не первая."""
    user, _, ascents = group_data
    user.experience_level = 3

    ascents.append(
        SimpleNamespace(
            mountain=SimpleNamespace(difficulty_level=5)
        )
    )

    result, reason = ascent_service.can_climber_join_group(1, 10)

    assert result is False
    assert "минимум 5" in reason