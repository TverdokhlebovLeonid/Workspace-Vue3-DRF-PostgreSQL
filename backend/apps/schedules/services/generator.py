from datetime import date, timedelta
from uuid import UUID

from django.db import transaction

from apps.schedules.models import Employee, Location, ScheduleShift
from apps.schedules.services.constants import DAYS_IN_GRID
from apps.schedules.services.period import ensure_current_period
from apps.schedules.services.rules import (
    is_available_by_cycle,
    is_filler_employee,
    is_primary_employee,
    would_exceed_max_consecutive,
)


def monday_on_or_before(day: date) -> date:
    return day - timedelta(days=day.weekday())


def monday_on_or_after(day: date) -> date:
    weekday = day.weekday()
    if weekday == 0:
        return day
    return day + timedelta(days=7 - weekday)


def default_grid_start(reference: date | None = None) -> date:
    return monday_on_or_before(reference or date.today())


def daterange(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def count_assignments(employee_id: UUID, assignments: dict[tuple[date, UUID], UUID]) -> int:
    return sum(1 for assigned_id in assignments.values() if assigned_id == employee_id)


def _employee_location_ids(employee: Employee) -> set[UUID]:
    return {location.id for location in employee.locations.all()}


def _pick_candidate(
    employees: list[Employee],
    *,
    day: date,
    location_id: UUID,
    assignments: dict[tuple[date, UUID], UUID],
    busy_on_day: dict[date, set[UUID]],
    primary_only: bool,
    require_cycle: bool,
) -> Employee | None:
    candidates: list[Employee] = []
    for employee in employees:
        if primary_only and (not is_primary_employee(employee)):
            continue
        if not primary_only and (not is_filler_employee(employee)):
            continue
        if location_id not in _employee_location_ids(employee):
            continue
        if employee.id in busy_on_day.get(day, set()):
            continue
        if require_cycle and (not is_available_by_cycle(employee, day)):
            continue
        if would_exceed_max_consecutive(employee, location_id, day, assignments):
            continue
        candidates.append(employee)
    if not candidates:
        return None
    return min(candidates, key=lambda emp: count_assignments(emp.id, assignments))


def _assign(
    day: date,
    location_id: UUID,
    employee: Employee,
    assignments: dict[tuple[date, UUID], UUID],
    busy_on_day: dict[date, set[UUID]],
) -> None:
    assignments[day, location_id] = employee.id
    busy_on_day.setdefault(day, set()).add(employee.id)


@transaction.atomic
def generate_schedule(start_date: date, days: int = DAYS_IN_GRID) -> int:
    end_date = start_date + timedelta(days=days - 1)
    locations = list(Location.objects.filter(is_active=True).order_by('sort_order', 'name'))
    employees = list(
        Employee.objects.filter(is_active=True)
        .prefetch_related('locations', 'work_rules')
        .order_by('id')
    )
    assignments: dict[tuple[date, UUID], UUID] = {}
    busy_on_day: dict[date, set[UUID]] = {}
    for day in daterange(start_date, end_date):
        for location in locations:
            location_id = location.id
            if (day, location_id) in assignments:
                continue
            chosen = _pick_candidate(
                employees,
                day=day,
                location_id=location_id,
                assignments=assignments,
                busy_on_day=busy_on_day,
                primary_only=True,
                require_cycle=True,
            )
            if chosen:
                _assign(day, location_id, chosen, assignments, busy_on_day)
    for day in daterange(start_date, end_date):
        for location in locations:
            location_id = location.id
            if (day, location_id) in assignments:
                continue
            chosen = _pick_candidate(
                employees,
                day=day,
                location_id=location_id,
                assignments=assignments,
                busy_on_day=busy_on_day,
                primary_only=False,
                require_cycle=False,
            )
            if chosen:
                _assign(day, location_id, chosen, assignments, busy_on_day)
    ScheduleShift.objects.filter(date__gte=start_date, date__lte=end_date).delete()
    period = ensure_current_period(start_date)
    shifts = [
        ScheduleShift(date=day, location_id=location_id, employee_id=employee_id, period=period)
        for (day, location_id), employee_id in assignments.items()
    ]
    ScheduleShift.objects.bulk_create(shifts)
    return len(shifts)
