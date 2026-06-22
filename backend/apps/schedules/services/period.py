from datetime import date, timedelta

from apps.schedules.models import SchedulePeriod
from apps.schedules.services.constants import DAYS_IN_GRID


def resolve_grid_start(start_param: date | None = None) -> date:
    from apps.schedules.services.generator import default_grid_start

    if start_param is not None:
        return default_grid_start(start_param)
    period = SchedulePeriod.objects.filter(is_current=True).first()
    if period:
        return period.start_date
    return default_grid_start()


def ensure_current_period(start_date: date) -> SchedulePeriod:
    end_date = start_date + timedelta(days=DAYS_IN_GRID - 1)
    year = start_date.year
    SchedulePeriod.objects.filter(is_current=True).exclude(year=year).update(is_current=False)
    period, _ = SchedulePeriod.objects.update_or_create(
        year=year, defaults={'start_date': start_date, 'end_date': end_date, 'is_current': True}
    )
    return period


def get_current_period() -> SchedulePeriod | None:
    return SchedulePeriod.objects.filter(is_current=True).first()
