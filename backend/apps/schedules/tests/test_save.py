from datetime import date, timedelta
from uuid import uuid4

import pytest
from rest_framework.exceptions import ValidationError

from apps.schedules.models import Employee, Location, SchedulePeriod, ScheduleShift
from apps.schedules.services.constants import DAYS_IN_GRID
from apps.schedules.services.save import apply_schedule_changes


def _create_location(*, is_active: bool = True) -> Location:
    return Location.objects.create(name=f'loc-{uuid4().hex[:6]}', is_active=is_active)


def _create_employee(*, is_active: bool = True) -> Employee:
    return Employee.objects.create(
        last_name='Test',
        first_name='User',
        nickname=f'emp-{uuid4().hex[:8]}',
        is_active=is_active,
    )


def _create_period(start_date: date) -> SchedulePeriod:
    return SchedulePeriod.objects.create(
        year=start_date.year,
        start_date=start_date,
        end_date=start_date + timedelta(days=DAYS_IN_GRID - 1),
        is_current=True,
    )


@pytest.fixture
def schedule_setup(db):
    start_date = date(2025, 6, 9)
    period = _create_period(start_date)
    location = _create_location()
    employee = _create_employee()
    employee.locations.add(location)
    shift_date = start_date + timedelta(days=3)
    return {
        'period': period,
        'location': location,
        'employee': employee,
        'shift_date': shift_date,
    }


@pytest.mark.django_db
def test_apply_schedule_changes_creates_shift(schedule_setup):
    saved = apply_schedule_changes(
        [
            {
                'date': schedule_setup['shift_date'],
                'location_id': schedule_setup['location'].id,
                'employee_id': schedule_setup['employee'].id,
            }
        ]
    )
    shift = ScheduleShift.objects.get(
        date=schedule_setup['shift_date'],
        location=schedule_setup['location'],
    )
    assert saved == 1
    assert shift.employee_id == schedule_setup['employee'].id
    assert shift.period_id == schedule_setup['period'].id


@pytest.mark.django_db
def test_apply_schedule_changes_updates_existing_shift(schedule_setup):
    other_employee = _create_employee()
    other_employee.locations.add(schedule_setup['location'])
    ScheduleShift.objects.create(
        date=schedule_setup['shift_date'],
        location=schedule_setup['location'],
        employee=schedule_setup['employee'],
        period=schedule_setup['period'],
    )
    saved = apply_schedule_changes(
        [
            {
                'date': schedule_setup['shift_date'],
                'location_id': schedule_setup['location'].id,
                'employee_id': other_employee.id,
            }
        ]
    )
    shift = ScheduleShift.objects.get(
        date=schedule_setup['shift_date'],
        location=schedule_setup['location'],
    )
    assert saved == 1
    assert shift.employee_id == other_employee.id


@pytest.mark.django_db
def test_apply_schedule_changes_clears_shift(schedule_setup):
    ScheduleShift.objects.create(
        date=schedule_setup['shift_date'],
        location=schedule_setup['location'],
        employee=schedule_setup['employee'],
        period=schedule_setup['period'],
    )
    saved = apply_schedule_changes(
        [
            {
                'date': schedule_setup['shift_date'],
                'location_id': schedule_setup['location'].id,
                'employee_id': None,
            }
        ]
    )
    assert saved == 1
    assert not ScheduleShift.objects.filter(
        date=schedule_setup['shift_date'],
        location=schedule_setup['location'],
    ).exists()


@pytest.mark.django_db
def test_apply_schedule_changes_clear_without_existing_shift(schedule_setup):
    saved = apply_schedule_changes(
        [
            {
                'date': schedule_setup['shift_date'],
                'location_id': schedule_setup['location'].id,
                'employee_id': None,
            }
        ]
    )
    assert saved == 0


@pytest.mark.django_db
def test_apply_schedule_changes_rejects_date_outside_period(schedule_setup):
    with pytest.raises(ValidationError, match='outside the current schedule'):
        apply_schedule_changes(
            [
                {
                    'date': schedule_setup['period'].end_date + timedelta(days=1),
                    'location_id': schedule_setup['location'].id,
                    'employee_id': schedule_setup['employee'].id,
                }
            ]
        )


@pytest.mark.django_db
def test_apply_schedule_changes_rejects_inactive_location(schedule_setup):
    location = _create_location(is_active=False)
    with pytest.raises(ValidationError, match='not found or inactive'):
        apply_schedule_changes(
            [
                {
                    'date': schedule_setup['shift_date'],
                    'location_id': location.id,
                    'employee_id': schedule_setup['employee'].id,
                }
            ]
        )


@pytest.mark.django_db
def test_apply_schedule_changes_rejects_missing_location(schedule_setup):
    with pytest.raises(ValidationError, match='not found or inactive'):
        apply_schedule_changes(
            [
                {
                    'date': schedule_setup['shift_date'],
                    'location_id': uuid4(),
                    'employee_id': schedule_setup['employee'].id,
                }
            ]
        )


@pytest.mark.django_db
def test_apply_schedule_changes_rejects_inactive_employee(schedule_setup):
    employee = _create_employee(is_active=False)
    employee.locations.add(schedule_setup['location'])
    with pytest.raises(ValidationError, match='not found or inactive'):
        apply_schedule_changes(
            [
                {
                    'date': schedule_setup['shift_date'],
                    'location_id': schedule_setup['location'].id,
                    'employee_id': employee.id,
                }
            ]
        )


@pytest.mark.django_db
def test_apply_schedule_changes_rejects_missing_employee(schedule_setup):
    with pytest.raises(ValidationError, match='not found or inactive'):
        apply_schedule_changes(
            [
                {
                    'date': schedule_setup['shift_date'],
                    'location_id': schedule_setup['location'].id,
                    'employee_id': uuid4(),
                }
            ]
        )


@pytest.mark.django_db
def test_apply_schedule_changes_rejects_employee_not_assigned_to_location(schedule_setup):
    employee = _create_employee()
    with pytest.raises(ValidationError, match='is not assigned to location'):
        apply_schedule_changes(
            [
                {
                    'date': schedule_setup['shift_date'],
                    'location_id': schedule_setup['location'].id,
                    'employee_id': employee.id,
                }
            ]
        )


@pytest.mark.django_db
def test_apply_schedule_changes_employee_location_error_is_structured(schedule_setup):
    employee = _create_employee()
    with pytest.raises(ValidationError) as exc_info:
        apply_schedule_changes(
            [
                {
                    'date': schedule_setup['shift_date'],
                    'location_id': schedule_setup['location'].id,
                    'employee_id': employee.id,
                }
            ]
        )
    detail = exc_info.value.detail
    assert detail['code'] == 'employee_not_assigned_to_location'
    assert detail['employee_nickname'] == employee.nickname
    assert detail['location_name'] == schedule_setup['location'].name
    assert detail['date'] == schedule_setup['shift_date'].isoformat()


@pytest.mark.django_db
def test_apply_schedule_changes_handles_multiple_changes(schedule_setup):
    second_location = _create_location()
    second_employee = _create_employee()
    second_employee.locations.add(second_location)
    ScheduleShift.objects.create(
        date=schedule_setup['shift_date'],
        location=schedule_setup['location'],
        employee=schedule_setup['employee'],
        period=schedule_setup['period'],
    )
    saved = apply_schedule_changes(
        [
            {
                'date': schedule_setup['shift_date'],
                'location_id': schedule_setup['location'].id,
                'employee_id': None,
            },
            {
                'date': schedule_setup['shift_date'] + timedelta(days=1),
                'location_id': schedule_setup['location'].id,
                'employee_id': schedule_setup['employee'].id,
            },
            {
                'date': schedule_setup['shift_date'] + timedelta(days=1),
                'location_id': second_location.id,
                'employee_id': second_employee.id,
            },
        ]
    )
    assert saved == 3
    assert ScheduleShift.objects.count() == 2
