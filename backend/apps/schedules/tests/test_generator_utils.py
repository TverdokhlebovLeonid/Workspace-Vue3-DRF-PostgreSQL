from datetime import date, timedelta
from unittest.mock import patch
from uuid import uuid4

import pytest

from apps.schedules.services.generator import (
    count_assignments,
    daterange,
    default_grid_start,
    monday_on_or_after,
    monday_on_or_before,
)


@pytest.mark.parametrize(
    ('day', 'expected'),
    [
        (date(2025, 6, 11), date(2025, 6, 9)),
        (date(2025, 6, 9), date(2025, 6, 9)),
    ],
)
def test_monday_on_or_before(day, expected):
    assert monday_on_or_before(day) == expected


@pytest.mark.parametrize(
    ('day', 'expected'),
    [
        (date(2025, 6, 11), date(2025, 6, 16)),
        (date(2025, 6, 9), date(2025, 6, 9)),
    ],
)
def test_monday_on_or_after(day, expected):
    assert monday_on_or_after(day) == expected


def test_default_grid_start_normalizes_to_monday():
    assert default_grid_start(date(2025, 6, 15)) == date(2025, 6, 9)


@patch('apps.schedules.services.generator.date')
def test_default_grid_start_uses_today_when_reference_missing(mock_date):
    mock_date.today.return_value = date(2025, 6, 15)
    assert default_grid_start() == date(2025, 6, 9)


def test_daterange_is_inclusive():
    start = date(2025, 6, 1)
    end = date(2025, 6, 3)
    assert list(daterange(start, end)) == [start, date(2025, 6, 2), end]


def test_count_assignments():
    employee_id = uuid4()
    other_id = uuid4()
    location_id = uuid4()
    day = date(2025, 6, 10)
    assignments = {
        (day, location_id): employee_id,
        (day + timedelta(days=1), location_id): employee_id,
        (day + timedelta(days=2), location_id): other_id,
    }
    assert count_assignments(employee_id, assignments) == 2
