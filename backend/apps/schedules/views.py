from datetime import date, datetime

from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsAdminRole, IsAuthenticatedReadOnly
from apps.schedules.models import Employee, Location, WorkRule
from apps.schedules.serializers import (
    EmployeeSerializer,
    LocationSerializer,
    ScheduleBulkSaveSerializer,
    WorkRuleSerializer,
)
from apps.schedules.services.employee_users import delete_employee_user
from apps.schedules.services.generator import DAYS_IN_GRID, generate_schedule
from apps.schedules.services.grid import build_schedule_grid, build_schedule_history
from apps.schedules.services.period import resolve_grid_start
from apps.schedules.services.save import apply_schedule_changes

MIN_HISTORY_WEEKS = 1
MAX_HISTORY_WEEKS = 12


def _parse_date_param(raw: str, field_name: str = 'date') -> date:
    try:
        return datetime.strptime(raw, '%Y-%m-%d').date()
    except ValueError as exc:
        raise ValidationError({field_name: 'Invalid date format. Use YYYY-MM-DD.'}) from exc


def _resolve_start(raw: str | None):
    if raw:
        return resolve_grid_start(_parse_date_param(raw, 'start'))
    return resolve_grid_start()


def _parse_history_weeks(raw: str | None) -> int:
    if raw is None or raw == '':
        return 2
    try:
        weeks = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValidationError({'weeks': 'Must be an integer.'}) from exc
    if weeks < MIN_HISTORY_WEEKS or weeks > MAX_HISTORY_WEEKS:
        raise ValidationError(
            {'weeks': f'Must be between {MIN_HISTORY_WEEKS} and {MAX_HISTORY_WEEKS}.'}
        )
    return weeks


class LocationListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticatedReadOnly,)
    serializer_class = LocationSerializer
    queryset = Location.objects.all().order_by('sort_order', 'name')


class LocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedReadOnly,)
    serializer_class = LocationSerializer
    queryset = Location.objects.all()


class WorkRuleListView(generics.ListAPIView):
    permission_classes = (IsAuthenticatedReadOnly,)
    serializer_class = WorkRuleSerializer
    queryset = WorkRule.objects.all()
    pagination_class = None


class EmployeeListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticatedReadOnly,)
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.prefetch_related('locations', 'work_rules').select_related('user')


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedReadOnly,)
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.prefetch_related('locations', 'work_rules').select_related('user')

    def perform_destroy(self, instance):
        delete_employee_user(instance)


class ScheduleGridView(APIView):
    permission_classes = (IsAuthenticatedReadOnly,)

    @extend_schema(responses={200: dict})
    def get(self, request):
        current_start = _resolve_start(request.query_params.get('start'))
        return Response(build_schedule_grid(current_start))


class ScheduleGridHistoryView(APIView):
    permission_classes = (IsAuthenticatedReadOnly,)

    @extend_schema(responses={200: dict})
    def get(self, request):
        before_param = request.query_params.get('before')
        if not before_param:
            return Response(
                {'detail': 'Query param "before" is required (YYYY-MM-DD).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        before_date = _parse_date_param(before_param, 'before')
        weeks = _parse_history_weeks(request.query_params.get('weeks'))
        return Response(build_schedule_history(before_date, weeks=weeks))


class ScheduleGenerateView(APIView):
    permission_classes = (IsAdminRole,)

    @extend_schema(request=None, responses={200: dict})
    def post(self, request):
        start_param = request.data.get('start') if isinstance(request.data, dict) else None
        current_start = _resolve_start(start_param)
        created = generate_schedule(current_start, days=DAYS_IN_GRID)
        grid = build_schedule_grid(current_start)
        return Response({'created_shifts': created, 'grid': grid}, status=status.HTTP_200_OK)


class ScheduleBulkSaveView(APIView):
    permission_classes = (IsAdminRole,)

    @extend_schema(request=ScheduleBulkSaveSerializer, responses={200: dict})
    def post(self, request):
        serializer = ScheduleBulkSaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved = apply_schedule_changes(serializer.validated_data['changes'])
        current_start = resolve_grid_start()
        grid = build_schedule_grid(current_start)
        return Response({'saved': saved, 'grid': grid}, status=status.HTTP_200_OK)
