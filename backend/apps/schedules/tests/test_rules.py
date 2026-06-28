from datetime import date, timedelta
from uuid import uuid4

import pytest

from apps.schedules.models import Employee, RuleKind, WorkRule, WorkRuleCode
from apps.schedules.services.rules import (
    is_available_by_cycle,
    is_filler_employee,
    is_primary_employee,
    would_exceed_max_consecutive,
)


def _create_rule(code: str, *, kind: str = RuleKind.CYCLE) -> WorkRule:
    return WorkRule.objects.create(code=code, name=code, kind=kind)


def _create_employee(*rule_codes: str, cycle_start_date: date | None = None) -> Employee:
    employee = Employee.objects.create(
        last_name='Test',
        first_name='User',
        nickname=f'emp-{uuid4().hex[:8]}',
        cycle_start_date=cycle_start_date,
    )
    for code in rule_codes:
        employee.work_rules.add(_create_rule(code))
    return employee


@pytest.mark.parametrize(
    ('rule_codes', 'expected_filler', 'expected_primary'),
    [
        ([], False, True),
        ([WorkRuleCode.MAX_2_CONSECUTIVE], True, False),
    ],
)
@pytest.mark.django_db
def test_employee_type_by_work_rules(rule_codes, expected_filler, expected_primary):
    employee = _create_employee(*rule_codes)
    assert is_filler_employee(employee) is expected_filler
    assert is_primary_employee(employee) is expected_primary


@pytest.mark.django_db
def test_is_available_without_cycle_rules():
    employee = _create_employee()
    assert is_available_by_cycle(employee, date(2025, 6, 10)) is True


@pytest.mark.django_db
def test_work_2_on_2_allows_work_days():
    anchor = date(2025, 6, 2)
    employee = _create_employee(WorkRuleCode.WORK_2_ON_2, cycle_start_date=anchor)
    assert is_available_by_cycle(employee, anchor) is True
    assert is_available_by_cycle(employee, anchor + timedelta(days=1)) is True


@pytest.mark.django_db
def test_work_2_on_2_blocks_off_days():
    anchor = date(2025, 6, 2)
    employee = _create_employee(WorkRuleCode.WORK_2_ON_2, cycle_start_date=anchor)
    assert is_available_by_cycle(employee, anchor + timedelta(days=2)) is False
    assert is_available_by_cycle(employee, anchor + timedelta(days=3)) is False


@pytest.mark.django_db
def test_work_3_on_2_allows_work_days():
    anchor = date(2025, 6, 2)
    employee = _create_employee(WorkRuleCode.WORK_3_ON_2, cycle_start_date=anchor)
    assert is_available_by_cycle(employee, anchor + timedelta(days=2)) is True


@pytest.mark.django_db
def test_work_3_on_2_blocks_off_days():
    anchor = date(2025, 6, 2)
    employee = _create_employee(WorkRuleCode.WORK_3_ON_2, cycle_start_date=anchor)
    assert is_available_by_cycle(employee, anchor + timedelta(days=3)) is False


@pytest.mark.django_db
def test_is_available_uses_cycle_start_date_as_anchor():
    anchor = date(2025, 1, 6)
    employee = _create_employee(WorkRuleCode.WORK_2_ON_2, cycle_start_date=anchor)
    day = date(2025, 2, 10)
    assert is_available_by_cycle(employee, day) is False


@pytest.mark.django_db
def test_is_available_requires_all_cycle_rules():
    anchor = date(2025, 6, 2)
    employee = _create_employee(
        WorkRuleCode.WORK_2_ON_2,
        WorkRuleCode.WORK_3_ON_2,
        cycle_start_date=anchor,
    )
    assert is_available_by_cycle(employee, anchor) is True
    assert is_available_by_cycle(employee, anchor + timedelta(days=2)) is False


@pytest.mark.django_db
def test_would_exceed_max_consecutive_without_rule():
    employee = _create_employee()
    location_id = uuid4()
    day = date(2025, 6, 10)
    assignments = {
        (day - timedelta(days=1), location_id): employee.id,
        (day - timedelta(days=2), location_id): employee.id,
    }
    assert would_exceed_max_consecutive(employee, location_id, day, assignments) is False


@pytest.mark.django_db
def test_would_exceed_max_consecutive_after_one_day():
    employee = _create_employee(WorkRuleCode.MAX_2_CONSECUTIVE)
    location_id = uuid4()
    day = date(2025, 6, 10)
    assignments = {(day - timedelta(days=1), location_id): employee.id}
    assert would_exceed_max_consecutive(employee, location_id, day, assignments) is False


@pytest.mark.django_db
def test_would_exceed_max_consecutive_after_two_days_on_same_location():
    employee = _create_employee(WorkRuleCode.MAX_2_CONSECUTIVE)
    location_id = uuid4()
    day = date(2025, 6, 10)
    assignments = {
        (day - timedelta(days=1), location_id): employee.id,
        (day - timedelta(days=2), location_id): employee.id,
    }
    assert would_exceed_max_consecutive(employee, location_id, day, assignments) is True


@pytest.mark.django_db
def test_would_exceed_max_consecutive_ignores_other_locations():
    employee = _create_employee(WorkRuleCode.MAX_2_CONSECUTIVE)
    location_id = uuid4()
    other_location_id = uuid4()
    day = date(2025, 6, 10)
    assignments = {
        (day - timedelta(days=1), location_id): employee.id,
        (day - timedelta(days=2), other_location_id): employee.id,
    }
    assert would_exceed_max_consecutive(employee, location_id, day, assignments) is False
