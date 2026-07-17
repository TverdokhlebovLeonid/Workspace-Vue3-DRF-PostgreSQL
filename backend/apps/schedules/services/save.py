from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.schedules.models import Employee, Location, ScheduleShift
from apps.schedules.services.period import get_current_period


def _raise_schedule_error(*, code: str, detail: str, **extra) -> None:
    raise ValidationError({'detail': detail, 'code': code, **extra})


@transaction.atomic
def apply_schedule_changes(changes: list[dict]) -> int:
    period = get_current_period()
    saved = 0
    for item in changes:
        shift_date = item['date']
        location_id = item['location_id']
        employee_id = item.get('employee_id')
        if period and (not period.start_date <= shift_date <= period.end_date):
            _raise_schedule_error(
                code='date_outside_period',
                detail=(
                    f'Date {shift_date} is outside the current schedule '
                    f'({period.start_date} — {period.end_date}).'
                ),
                date=shift_date.isoformat(),
            )
        try:
            location = Location.objects.get(pk=location_id, is_active=True)
        except Location.DoesNotExist as exc:
            raise ValidationError(f'Location id={location_id} not found or inactive.') from exc
        if employee_id is None:
            deleted, _ = ScheduleShift.objects.filter(
                date=shift_date, location_id=location_id
            ).delete()
            if deleted:
                saved += 1
            continue
        try:
            employee = Employee.objects.get(pk=employee_id, is_active=True)
        except Employee.DoesNotExist as exc:
            raise ValidationError(f'Employee id={employee_id} not found or inactive.') from exc
        if not employee.locations.filter(pk=location_id).exists():
            _raise_schedule_error(
                code='employee_not_assigned_to_location',
                detail=(
                    f'Employee "{employee.nickname}" is not assigned to location "{location.name}".'
                ),
                date=shift_date.isoformat(),
                location_id=str(location_id),
                location_name=location.name,
                employee_id=str(employee_id),
                employee_nickname=employee.nickname,
            )
        defaults = {'employee_id': employee_id}
        if period:
            defaults['period_id'] = period.pk
        ScheduleShift.objects.update_or_create(
            date=shift_date, location_id=location_id, defaults=defaults
        )
        saved += 1
    return saved
