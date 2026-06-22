from datetime import date, timedelta
from uuid import UUID

from apps.schedules.models import Location, ScheduleShift
from apps.schedules.services.constants import DAYS_IN_GRID, PAST_WEEKS, WEEKS_IN_GRID
from apps.schedules.services.period import get_current_period

WEEKDAY_LABELS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')


def _build_weeks(
    start_date: date,
    weeks_count: int,
    *,
    is_past: bool,
    shift_map: dict[tuple[date, UUID], ScheduleShift],
    locations: list[Location],
) -> list[dict]:
    weeks: list[dict] = []
    for week_index in range(weeks_count):
        week_start = start_date + timedelta(days=week_index * 7)
        week_dates = [week_start + timedelta(days=offset) for offset in range(7)]
        days = [
            {
                'date': day.isoformat(),
                'weekday': day.weekday(),
                'weekday_label': WEEKDAY_LABELS[day.weekday()],
                'display': day.strftime('%d.%m.%Y'),
            }
            for day in week_dates
        ]
        rows = []
        for location in locations:
            cells = []
            for day in week_dates:
                shift = shift_map.get((day, location.id))
                cells.append(
                    {
                        'date': day.isoformat(),
                        'employee_id': shift.employee_id if shift else None,
                        'nickname': shift.employee.nickname if shift else '',
                    }
                )
            rows.append(
                {
                    'location': {
                        'id': location.id,
                        'name': location.name,
                        'location_type': location.location_type,
                        'location_type_label': location.get_location_type_display(),
                    },
                    'cells': cells,
                }
            )
        weeks.append(
            {
                'week_index': week_index + 1,
                'week_start': week_start.isoformat(),
                'is_past': is_past,
                'days': days,
                'rows': rows,
            }
        )
    return weeks


def _load_shift_map(date_from: date, date_to: date) -> dict[tuple[date, UUID], ScheduleShift]:
    shifts = ScheduleShift.objects.filter(date__gte=date_from, date__lte=date_to).select_related(
        'employee', 'location'
    )
    return {(shift.date, shift.location_id): shift for shift in shifts}


def build_schedule_grid(start_date: date) -> dict:
    end_date = start_date + timedelta(days=DAYS_IN_GRID - 1)
    period = get_current_period()
    year = period.year if period else start_date.year
    locations = list(Location.objects.filter(is_active=True).order_by('sort_order', 'name'))
    shift_map = _load_shift_map(start_date, end_date)
    weeks = _build_weeks(
        start_date, WEEKS_IN_GRID, is_past=False, shift_map=shift_map, locations=locations
    )
    return {
        'year': year,
        'current_start_date': start_date.isoformat(),
        'current_end_date': end_date.isoformat(),
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'weeks_count': WEEKS_IN_GRID,
        'days_count': DAYS_IN_GRID,
        'weeks': weeks,
    }


def build_schedule_history(before_date: date, weeks: int = PAST_WEEKS) -> dict:
    history_start = before_date - timedelta(days=weeks * 7)
    history_end = before_date - timedelta(days=1)
    locations = list(Location.objects.filter(is_active=True).order_by('sort_order', 'name'))
    shift_map = _load_shift_map(history_start, history_end)
    history_weeks = _build_weeks(
        history_start, weeks, is_past=True, shift_map=shift_map, locations=locations
    )
    return {
        'before_date': before_date.isoformat(),
        'start_date': history_start.isoformat(),
        'end_date': history_end.isoformat(),
        'weeks_count': weeks,
        'weeks': history_weeks,
    }
