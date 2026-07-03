from datetime import date, timedelta
from uuid import uuid4

import pytest

from apps.schedules.models import Employee, Location, RuleKind, SchedulePeriod, ScheduleShift, WorkRule
from apps.schedules.models import WorkRuleCode
from apps.schedules.services.constants import DAYS_IN_GRID
from apps.schedules.services.generator import generate_schedule
from apps.schedules.services.period import get_current_period


def _create_location(*, is_active: bool = True) -> Location:
    return Location.objects.create(name=f'loc-{uuid4().hex[:6]}', is_active=is_active)


def _create_employee(*, is_active: bool = True) -> Employee:
    return Employee.objects.create(
        last_name='Test',
        first_name='User',
        nickname=f'emp-{uuid4().hex[:8]}',
        is_active=is_active,
    )


def _create_rule(code: str, *, kind: str = RuleKind.CYCLE) -> WorkRule:
    return WorkRule.objects.create(code=code, name=code, kind=kind)


@pytest.fixture
def start_date():
    return date(2025, 6, 9)


@pytest.mark.django_db
def test_generate_schedule_returns_zero_without_locations(start_date):
    _create_employee()
    assert generate_schedule(start_date) == 0
    assert ScheduleShift.objects.count() == 0


@pytest.mark.django_db
def test_generate_schedule_returns_zero_without_employees(start_date):
    _create_location()
    assert generate_schedule(start_date) == 0
    assert ScheduleShift.objects.count() == 0


@pytest.mark.django_db
def test_generate_schedule_creates_shift_for_each_day_and_location(start_date):
    location = _create_location()
    employee = _create_employee()
    employee.locations.add(location)
    created = generate_schedule(start_date)
    assert created == DAYS_IN_GRID
    assert ScheduleShift.objects.count() == DAYS_IN_GRID


@pytest.mark.django_db
def test_generate_schedule_links_shifts_to_current_period(start_date):
    location = _create_location()
    employee = _create_employee()
    employee.locations.add(location)
    generate_schedule(start_date)
    period = get_current_period()
    assert period is not None
    assert period.start_date == start_date
    assert period.is_current is True
    assert ScheduleShift.objects.filter(period=period).count() == DAYS_IN_GRID


@pytest.mark.django_db
def test_generate_schedule_prefers_primary_over_filler(start_date):
    location = _create_location()
    primary = _create_employee()
    filler = _create_employee()
    filler.work_rules.add(_create_rule(WorkRuleCode.MAX_2_CONSECUTIVE, kind=RuleKind.CONSTRAINT))
    primary.locations.add(location)
    filler.locations.add(location)
    generate_schedule(start_date)
    primary_count = ScheduleShift.objects.filter(employee=primary).count()
    filler_count = ScheduleShift.objects.filter(employee=filler).count()
    assert primary_count == DAYS_IN_GRID
    assert filler_count == 0


@pytest.mark.django_db
def test_generate_schedule_uses_filler_when_no_primary_available(start_date):
    location = _create_location()
    filler = _create_employee()
    filler.work_rules.add(_create_rule(WorkRuleCode.MAX_2_CONSECUTIVE, kind=RuleKind.CONSTRAINT))
    filler.locations.add(location)
    created = generate_schedule(start_date)
    assert 0 < created < DAYS_IN_GRID
    assert ScheduleShift.objects.filter(employee=filler).count() == created


@pytest.mark.django_db
def test_generate_schedule_does_not_assign_employee_outside_locations(start_date):
    location_a = _create_location()
    location_b = _create_location()
    employee = _create_employee()
    employee.locations.add(location_a)
    generate_schedule(start_date)
    assert ScheduleShift.objects.filter(location=location_a).count() == DAYS_IN_GRID
    assert ScheduleShift.objects.filter(location=location_b).count() == 0


@pytest.mark.django_db
def test_generate_schedule_prevents_same_employee_on_two_locations_same_day(start_date):
    location_a = _create_location()
    location_b = _create_location()
    employee = _create_employee()
    employee.locations.add(location_a, location_b)
    generate_schedule(start_date)
    for offset in range(DAYS_IN_GRID):
        day = start_date + timedelta(days=offset)
        assert ScheduleShift.objects.filter(date=day, employee=employee).count() == 1


@pytest.mark.django_db
def test_generate_schedule_replaces_existing_shifts_in_range(start_date):
    location = _create_location()
    old_employee = _create_employee()
    new_employee = _create_employee()
    old_employee.locations.add(location)
    period = SchedulePeriod.objects.create(
        year=start_date.year,
        start_date=start_date,
        end_date=start_date + timedelta(days=DAYS_IN_GRID - 1),
        is_current=True,
    )
    ScheduleShift.objects.create(
        date=start_date,
        location=location,
        employee=old_employee,
        period=period,
    )
    old_employee.is_active = False
    old_employee.save(update_fields=['is_active'])
    new_employee.locations.add(location)
    generate_schedule(start_date)
    assert ScheduleShift.objects.filter(employee=old_employee).count() == 0
    assert ScheduleShift.objects.filter(employee=new_employee).count() == DAYS_IN_GRID


@pytest.mark.django_db
def test_generate_schedule_ignores_inactive_locations_and_employees(start_date):
    active_location = _create_location()
    _create_location(is_active=False)
    active_employee = _create_employee()
    inactive_employee = _create_employee(is_active=False)
    active_employee.locations.add(active_location)
    inactive_employee.locations.add(active_location)
    created = generate_schedule(start_date)
    assert created == DAYS_IN_GRID
    assert ScheduleShift.objects.filter(employee=inactive_employee).count() == 0


@pytest.mark.django_db
def test_generate_schedule_leaves_gaps_when_cycle_blocks_primary_and_no_filler(start_date):
    location = _create_location()
    employee = _create_employee()
    employee.work_rules.add(_create_rule(WorkRuleCode.WORK_2_ON_2))
    employee.cycle_start_date = start_date
    employee.save(update_fields=['cycle_start_date'])
    employee.locations.add(location)
    created = generate_schedule(start_date)
    assert 0 < created < DAYS_IN_GRID
