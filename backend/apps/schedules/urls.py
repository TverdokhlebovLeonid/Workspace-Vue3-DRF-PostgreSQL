from django.urls import path

from apps.schedules.views import (
    EmployeeDetailView,
    EmployeeListCreateView,
    LocationDetailView,
    LocationListCreateView,
    ScheduleBulkSaveView,
    ScheduleGenerateView,
    ScheduleGridHistoryView,
    ScheduleGridView,
    WorkRuleListView,
)

urlpatterns = [
    path('locations/', LocationListCreateView.as_view(), name='schedule-locations'),
    path('locations/<uuid:pk>/', LocationDetailView.as_view(), name='schedule-location-detail'),
    path('work-rules/', WorkRuleListView.as_view(), name='schedule-work-rules'),
    path('employees/', EmployeeListCreateView.as_view(), name='schedule-employees'),
    path('employees/<uuid:pk>/', EmployeeDetailView.as_view(), name='schedule-employee-detail'),
    path('grid/', ScheduleGridView.as_view(), name='schedule-grid'),
    path('grid/history/', ScheduleGridHistoryView.as_view(), name='schedule-grid-history'),
    path('grid/save/', ScheduleBulkSaveView.as_view(), name='schedule-grid-save'),
    path('generate/', ScheduleGenerateView.as_view(), name='schedule-generate'),
]
