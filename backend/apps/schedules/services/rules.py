from datetime import date, timedelta
from uuid import UUID

from apps.schedules.models import Employee, WorkRuleCode

CYCLE_DEFINITIONS: dict[str, tuple[int, frozenset[int]]] = {
    WorkRuleCode.WORK_2_ON_2: (4, frozenset({0, 1})),
    WorkRuleCode.WORK_3_ON_2: (5, frozenset({0, 1, 2})),
}


def employee_rule_codes(employee: Employee) -> set[str]:
    return {rule.code for rule in employee.work_rules.all()}


def is_filler_employee(employee: Employee) -> bool:
    return WorkRuleCode.MAX_2_CONSECUTIVE in employee_rule_codes(employee)


def is_primary_employee(employee: Employee) -> bool:
    return not is_filler_employee(employee)


def is_available_by_cycle(employee: Employee, day: date) -> bool:
    codes = employee_rule_codes(employee)
    cycle_codes = codes & CYCLE_DEFINITIONS.keys()
    if not cycle_codes:
        return True
    anchor = employee.cycle_start_date or day
    for code in cycle_codes:
        period, work_positions = CYCLE_DEFINITIONS[code]
        delta_days = (day - anchor).days
        position = delta_days % period
        if position not in work_positions:
            return False
    return True


def would_exceed_max_consecutive(
    employee: Employee, location_id: UUID, day: date, assignments: dict[tuple[date, UUID], UUID]
) -> bool:
    if WorkRuleCode.MAX_2_CONSECUTIVE not in employee_rule_codes(employee):
        return False
    previous_day = day - timedelta(days=1)
    two_days_ago = day - timedelta(days=2)
    employee_id = employee.id
    worked_yesterday = assignments.get((previous_day, location_id)) == employee_id
    worked_two_days_ago = assignments.get((two_days_ago, location_id)) == employee_id
    return worked_yesterday and worked_two_days_ago
