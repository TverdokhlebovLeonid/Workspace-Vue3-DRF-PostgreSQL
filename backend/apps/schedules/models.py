from django.db import models

from apps.common.models import UUIDModel


class LocationType(models.TextChoices):
    STORE = ('STORE', 'Store')
    CASH_REGISTER = ('CASH_REGISTER', 'Cash register')


class RuleKind(models.TextChoices):
    CYCLE = ('CYCLE', 'Shift cycle')
    CONSTRAINT = ('CONSTRAINT', 'Constraint')


class WorkRuleCode(models.TextChoices):
    WORK_2_ON_2 = ('WORK_2_ON_2', '2 days on, 2 days off')
    WORK_3_ON_2 = ('WORK_3_ON_2', '3 days on, 2 days off')
    MAX_2_CONSECUTIVE = ('MAX_2_CONSECUTIVE', 'No more than 2 consecutive days')


class Location(UUIDModel):
    location_type = models.CharField(
        max_length=20, choices=LocationType.choices, default=LocationType.STORE
    )
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'location'
        verbose_name_plural = 'locations'

    def __str__(self) -> str:
        return self.name


class WorkRule(UUIDModel):
    code = models.CharField(max_length=40, choices=WorkRuleCode.choices, unique=True)
    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=20, choices=RuleKind.choices)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'work rule'
        verbose_name_plural = 'work rules'

    def __str__(self) -> str:
        return self.name


class Employee(UUIDModel):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=50, unique=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    locations = models.ManyToManyField(Location, related_name='employees', blank=True)
    work_rules = models.ManyToManyField(WorkRule, related_name='employees', blank=True)
    cycle_start_date = models.DateField(
        null=True, blank=True, help_text='Cycle start date for "2 on, 2 off" / "3 on, 2 off" rules.'
    )
    is_active = models.BooleanField(default=True)
    user = models.OneToOneField(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name', 'nickname']
        verbose_name = 'employee'
        verbose_name_plural = 'employees'

    def __str__(self) -> str:
        return self.nickname


class SchedulePeriod(UUIDModel):
    year = models.PositiveIntegerField(unique=True)
    start_date = models.DateField(help_text='Monday of the first week of the current schedule.')
    end_date = models.DateField(help_text='Last day of the current schedule (5 weeks).')
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year']
        verbose_name = 'schedule period'
        verbose_name_plural = 'schedule periods'

    def __str__(self) -> str:
        current = ' (current)' if self.is_current else ''
        return f'Schedule {self.year}{current}'


class ScheduleShift(UUIDModel):
    date = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='shifts')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='shifts')
    period = models.ForeignKey(
        SchedulePeriod, on_delete=models.SET_NULL, related_name='shifts', null=True, blank=True
    )

    class Meta:
        ordering = ['date', 'location__sort_order', 'location__name']
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'location'], name='unique_shift_per_location_day'
            )
        ]
        verbose_name = 'schedule shift'
        verbose_name_plural = 'schedule shifts'

    def __str__(self) -> str:
        return f'{self.date} {self.location}: {self.employee.nickname}'
