from datetime import date, timedelta
from unittest.mock import patch

import pytest

from apps.schedules.models import SchedulePeriod
from apps.schedules.services.constants import DAYS_IN_GRID
from apps.schedules.services.period import ensure_current_period, get_current_period, resolve_grid_start


@pytest.mark.django_db
def test_resolve_grid_start_with_explicit_date():
    assert resolve_grid_start(date(2025, 6, 15)) == date(2025, 6, 9)


@pytest.mark.django_db
def test_resolve_grid_start_uses_current_period():
    SchedulePeriod.objects.create(
        year=2025,
        start_date=date(2025, 1, 6),
        end_date=date(2025, 2, 9),
        is_current=True,
    )
    assert resolve_grid_start() == date(2025, 1, 6)


@pytest.mark.django_db
@patch('apps.schedules.services.generator.default_grid_start', return_value=date(2025, 6, 9))
def test_resolve_grid_start_falls_back_to_default(mock_default_grid_start):
    assert resolve_grid_start() == date(2025, 6, 9)
    mock_default_grid_start.assert_called_once_with()


@pytest.mark.django_db
def test_ensure_current_period_creates_period():
    start_date = date(2025, 6, 9)
    period = ensure_current_period(start_date)
    assert period.year == 2025
    assert period.start_date == start_date
    assert period.end_date == start_date + timedelta(days=DAYS_IN_GRID - 1)
    assert period.is_current is True


@pytest.mark.django_db
def test_ensure_current_period_updates_existing_year():
    start_date = date(2025, 6, 9)
    SchedulePeriod.objects.create(
        year=2025,
        start_date=date(2025, 1, 6),
        end_date=date(2025, 2, 9),
        is_current=False,
    )
    period = ensure_current_period(start_date)
    assert period.start_date == start_date
    assert SchedulePeriod.objects.filter(year=2025).count() == 1


@pytest.mark.django_db
def test_ensure_current_period_clears_other_years():
    SchedulePeriod.objects.create(
        year=2024,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 2, 4),
        is_current=True,
    )
    ensure_current_period(date(2025, 6, 9))
    assert SchedulePeriod.objects.get(year=2024).is_current is False
    assert SchedulePeriod.objects.get(year=2025).is_current is True


@pytest.mark.django_db
def test_get_current_period():
    assert get_current_period() is None
    current = SchedulePeriod.objects.create(
        year=2025,
        start_date=date(2025, 6, 9),
        end_date=date(2025, 7, 13),
        is_current=True,
    )
    assert get_current_period() == current
