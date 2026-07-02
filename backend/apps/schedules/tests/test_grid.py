from datetime import date, timedelta
from uuid import uuid4

import pytest

from apps.schedules.models import Employee, Location, SchedulePeriod, ScheduleShift
from apps.schedules.services.constants import DAYS_IN_GRID, PAST_WEEKS, WEEKS_IN_GRID
from apps.schedules.services.grid import build_schedule_grid, build_schedule_history


def _create_location(*, name: str | None = None, sort_order: int = 0, is_active: bool = True) -> Location:
    return Location.objects.create(
        name=name or f'loc-{uuid4().hex[:6]}',
        sort_order=sort_order,
        is_active=is_active,
    )


def _create_employee(nickname: str | None = None) -> Employee:
    return Employee.objects.create(
        last_name='Test',
        first_name='User',
        nickname=nickname or f'emp-{uuid4().hex[:8]}',
    )


def _create_period(start_date: date) -> SchedulePeriod:
    return SchedulePeriod.objects.create(
        year=start_date.year,
        start_date=start_date,
        end_date=start_date + timedelta(days=DAYS_IN_GRID - 1),
        is_current=True,
    )


@pytest.fixture
def grid_setup(db):
    start_date = date(2025, 6, 9)
    period = _create_period(start_date)
    active_location = _create_location(name='Active', sort_order=1)
    _create_location(name='Inactive', sort_order=0, is_active=False)
    employee = _create_employee(nickname='Sasha')
    ScheduleShift.objects.create(
        date=start_date,
        location=active_location,
        employee=employee,
        period=period,
    )
    return {
        'start_date': start_date,
        'period': period,
        'active_location': active_location,
        'employee': employee,
    }


@pytest.mark.django_db
def test_build_schedule_grid_metadata(grid_setup):
    grid = build_schedule_grid(grid_setup['start_date'])
    end_date = grid_setup['start_date'] + timedelta(days=DAYS_IN_GRID - 1)
    assert grid['year'] == grid_setup['period'].year
    assert grid['weeks_count'] == WEEKS_IN_GRID
    assert grid['days_count'] == DAYS_IN_GRID
    assert grid['start_date'] == grid_setup['start_date'].isoformat()
    assert grid['end_date'] == end_date.isoformat()
    assert grid['current_start_date'] == grid_setup['start_date'].isoformat()
    assert grid['current_end_date'] == end_date.isoformat()


@pytest.mark.django_db
def test_build_schedule_grid_uses_start_date_year_without_period():
    start_date = date(2025, 6, 9)
    grid = build_schedule_grid(start_date)
    assert grid['year'] == 2025


@pytest.mark.django_db
def test_build_schedule_grid_week_structure(grid_setup):
    grid = build_schedule_grid(grid_setup['start_date'])
    assert len(grid['weeks']) == WEEKS_IN_GRID
    first_week = grid['weeks'][0]
    assert first_week['week_index'] == 1
    assert first_week['week_start'] == grid_setup['start_date'].isoformat()
    assert first_week['is_past'] is False
    assert len(first_week['days']) == 7
    assert first_week['days'][0]['weekday_label'] == 'Monday'


@pytest.mark.django_db
def test_build_schedule_grid_includes_shift_cell(grid_setup):
    grid = build_schedule_grid(grid_setup['start_date'])
    cell = grid['weeks'][0]['rows'][0]['cells'][0]
    assert cell['date'] == grid_setup['start_date'].isoformat()
    assert cell['employee_id'] == grid_setup['employee'].id
    assert cell['nickname'] == 'Sasha'


@pytest.mark.django_db
def test_build_schedule_grid_empty_cell_without_shift(grid_setup):
    grid = build_schedule_grid(grid_setup['start_date'])
    cell = grid['weeks'][0]['rows'][0]['cells'][1]
    assert cell['employee_id'] is None
    assert cell['nickname'] == ''


@pytest.mark.django_db
def test_build_schedule_grid_includes_only_active_locations():
    start_date = date(2025, 6, 9)
    active = _create_location(name='Open', sort_order=1)
    _create_location(name='Closed', sort_order=2, is_active=False)
    grid = build_schedule_grid(start_date)
    location_names = [row['location']['name'] for row in grid['weeks'][0]['rows']]
    assert location_names == ['Open']
    assert active.id in {row['location']['id'] for row in grid['weeks'][0]['rows']}


@pytest.mark.django_db
def test_build_schedule_grid_orders_locations_by_sort_order_and_name():
    start_date = date(2025, 6, 9)
    _create_location(name='Bravo', sort_order=2)
    _create_location(name='Zulu', sort_order=1)
    _create_location(name='Alpha', sort_order=1)
    grid = build_schedule_grid(start_date)
    location_names = [row['location']['name'] for row in grid['weeks'][0]['rows']]
    assert location_names == ['Alpha', 'Zulu', 'Bravo']


@pytest.mark.django_db
def test_build_schedule_history_metadata(grid_setup):
    before_date = grid_setup['start_date'] + timedelta(days=14)
    history = build_schedule_history(before_date)
    history_start = before_date - timedelta(days=PAST_WEEKS * 7)
    history_end = before_date - timedelta(days=1)
    assert history['before_date'] == before_date.isoformat()
    assert history['start_date'] == history_start.isoformat()
    assert history['end_date'] == history_end.isoformat()
    assert history['weeks_count'] == PAST_WEEKS


@pytest.mark.django_db
def test_build_schedule_history_marks_weeks_as_past(grid_setup):
    before_date = grid_setup['start_date'] + timedelta(days=14)
    history = build_schedule_history(before_date)
    assert all(week['is_past'] is True for week in history['weeks'])


@pytest.mark.django_db
def test_build_schedule_history_respects_custom_weeks_count(grid_setup):
    before_date = grid_setup['start_date'] + timedelta(days=21)
    history = build_schedule_history(before_date, weeks=3)
    assert history['weeks_count'] == 3
    assert len(history['weeks']) == 3


@pytest.mark.django_db
def test_build_schedule_history_includes_saved_shifts(grid_setup):
    before_date = grid_setup['start_date'] + timedelta(days=14)
    history_end = before_date - timedelta(days=1)
    employee = _create_employee(nickname='History')
    ScheduleShift.objects.create(
        date=history_end,
        location=grid_setup['active_location'],
        employee=employee,
        period=grid_setup['period'],
    )
    history = build_schedule_history(before_date)
    last_week = history['weeks'][-1]
    matching_cells = [
        cell
        for row in last_week['rows']
        for cell in row['cells']
        if cell['date'] == history_end.isoformat()
    ]
    assert any(cell['nickname'] == 'History' for cell in matching_cells)
