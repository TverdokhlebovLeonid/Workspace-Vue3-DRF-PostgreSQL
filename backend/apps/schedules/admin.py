from django.contrib import admin

from apps.schedules.models import Employee, Location, SchedulePeriod, ScheduleShift, WorkRule


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_type', 'is_active', 'sort_order')
    list_filter = ('location_type', 'is_active')
    search_fields = ('name',)


@admin.register(WorkRule)
class WorkRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'kind')
    list_filter = ('kind',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'last_name', 'first_name', 'phone', 'is_active')
    search_fields = ('nickname', 'last_name', 'first_name', 'email', 'phone')
    filter_horizontal = ('locations', 'work_rules')


@admin.register(SchedulePeriod)
class SchedulePeriodAdmin(admin.ModelAdmin):
    list_display = ('year', 'start_date', 'end_date', 'is_current', 'updated_at')
    list_filter = ('is_current',)
    ordering = ('-year',)


@admin.register(ScheduleShift)
class ScheduleShiftAdmin(admin.ModelAdmin):
    list_display = ('date', 'location', 'employee')
    list_filter = ('date', 'location')
    search_fields = ('employee__nickname', 'location__name')
    date_hierarchy = 'date'
