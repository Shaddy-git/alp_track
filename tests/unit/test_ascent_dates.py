from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from services import ascent_service

@pytest.fixture
def mock_group(monkeypatch):
    """Подменяет получение группы из базы данных."""
    group = SimpleNamespace(
        start_date=date(2026, 7, 10),
        end_date=date(2026, 7, 20),
    )

    fake_group_model = SimpleNamespace(
        query=SimpleNamespace(get=Mock(return_value=group))
    )

    monkeypatch.setattr(ascent_service, "Group", fake_group_model)
    return group

def test_date_inside_group_period(mock_group):
    """Дата внутри периода разрешена"""
    result, reason = ascent_service.validate_ascent_dates(
        1, date(2026, 7, 15)
    )

    assert result is True
    assert reason == ""

def test_date_before_group_start(mock_group):
    """Дата раньше начала группы запрещена"""
    result, reason = ascent_service.validate_ascent_dates(
        1, date(2026, 7, 9)
    )

    assert result is False
    assert "раньше" in reason

def test_date_after_group_end(mock_group):
    """Дата позже окнчания группы запрещена"""
    result, reason = ascent_service.validate_ascent_dates(
        1, date(2026, 7, 21)
    )
    
    assert result is False
    assert "позже" in reason

def test_date_equals_group_start(mock_group):
    """Первый день разрешен"""
    result, _ =ascent_service.validate_ascent_dates(
        1, date(2026, 7, 10)
    )

    assert result is True

def test_date_equals_group_end(mock_group):
    """Последний день разрешен"""
    result, _ =ascent_service.validate_ascent_dates(
        1, date(2026, 7, 20)
    )

    assert result is True

def test_group_not_found(monkeypatch):
    """Несуществующая группа должна вызывать отказ"""
    fake_group_model = SimpleNamespace(
        query=SimpleNamespace(get=Mock(return_value=None))
    )
    monkeypatch.setattr(ascent_service, "Group", fake_group_model)

    result, reason = ascent_service.validate_ascent_dates(
        999, date(2026, 7, 15)
    )

    assert result is False
    assert reason == "Группа не найдена"

def test_no_group_specified():
    """Без группы проверка периода не применяется"""
    result, reason = ascent_service.validate_ascent_dates(
        None, date(2026, 7, 15)
    )
    assert result is True
    assert reason == ""



