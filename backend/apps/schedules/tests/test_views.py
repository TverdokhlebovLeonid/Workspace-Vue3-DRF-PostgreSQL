from datetime import date, timedelta
from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework import status

from apps.schedules.models import (
    Employee,
    Location,
    RuleKind,
    SchedulePeriod,
    ScheduleShift,
    WorkRule,
    WorkRuleCode,
)
from apps.schedules.services.constants import DAYS_IN_GRID
from apps.users.models import User

LOCATIONS_URL = reverse('schedule-locations')
EMPLOYEES_URL = reverse('schedule-employees')
WORK_RULES_URL = reverse('schedule-work-rules')
GRID_URL = reverse('schedule-grid')
GRID_HISTORY_URL = reverse('schedule-grid-history')
GRID_SAVE_URL = reverse('schedule-grid-save')
GENERATE_URL = reverse('schedule-generate')


def location_detail_url(location_id):
    return reverse('schedule-location-detail', args=[location_id])


def employee_detail_url(employee_id):
    return reverse('schedule-employee-detail', args=[employee_id])


def _create_location(**overrides) -> Location:
    data = {
        'name': f'loc-{uuid4().hex[:6]}',
        'is_active': True,
        'sort_order': 0,
    }
    data.update(overrides)
    return Location.objects.create(**data)


def _create_employee(**overrides) -> Employee:
    data = {
        'last_name': 'Test',
        'first_name': 'User',
        'nickname': f'emp-{uuid4().hex[:8]}',
        'is_active': True,
    }
    data.update(overrides)
    return Employee.objects.create(**data)


def _create_work_rule() -> WorkRule:
    return WorkRule.objects.create(
        code=WorkRuleCode.WORK_2_ON_2,
        name='2/2',
        kind=RuleKind.CYCLE,
    )


def _create_period(start_date: date) -> SchedulePeriod:
    return SchedulePeriod.objects.create(
        year=start_date.year,
        start_date=start_date,
        end_date=start_date + timedelta(days=DAYS_IN_GRID - 1),
        is_current=True,
    )


@pytest.fixture
def grid_setup(db):
    start_date = date(2025, 6, 9)
    period = _create_period(start_date)
    location = _create_location(name='Active')
    employee = _create_employee(nickname='Sasha')
    ScheduleShift.objects.create(
        date=start_date,
        location=location,
        employee=employee,
        period=period,
    )
    return {
        'start_date': start_date,
        'period': period,
        'location': location,
        'employee': employee,
    }


@pytest.fixture
def schedule_setup(db):
    start_date = date(2025, 6, 9)
    period = _create_period(start_date)
    location = _create_location()
    employee = _create_employee()
    employee.locations.add(location)
    shift_date = start_date + timedelta(days=3)
    return {
        'start_date': start_date,
        'period': period,
        'location': location,
        'employee': employee,
        'shift_date': shift_date,
    }


@pytest.fixture
def generate_setup(db):
    start_date = date(2025, 6, 9)
    location = _create_location()
    employee = _create_employee()
    employee.locations.add(location)
    return {'start_date': start_date, 'location': location, 'employee': employee}


@pytest.mark.django_db
def test_locations_list_requires_authentication(api_client):
    response = api_client.get(LOCATIONS_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_locations_create_forbidden_for_regular_user(auth_client):
    response = auth_client.post(
        LOCATIONS_URL,
        {'name': 'New store', 'location_type': 'STORE', 'is_active': True, 'sort_order': 1},
        format='json',
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_create_location(admin_client):
    response = admin_client.post(
        LOCATIONS_URL,
        {'name': 'New store', 'location_type': 'STORE', 'is_active': True, 'sort_order': 1},
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert Location.objects.filter(name='New store').exists()


@pytest.mark.django_db
def test_employees_list_for_authenticated_user(auth_client, grid_setup):
    response = auth_client.get(EMPLOYEES_URL)
    assert response.status_code == status.HTTP_200_OK
    nicknames = {item['nickname'] for item in response.data['results']}
    assert grid_setup['employee'].nickname in nicknames


@pytest.mark.django_db
def test_admin_can_create_employee(admin_client):
    nickname = f'new-{uuid4().hex[:8]}'
    response = admin_client.post(
        EMPLOYEES_URL,
        {
            'last_name': 'Petrov',
            'first_name': 'Petr',
            'nickname': nickname,
            'email': 'petr@example.com',
            'password': 'password123',
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    employee = Employee.objects.get(nickname=nickname)
    user = User.objects.get(username=nickname)
    assert employee.user_id == user.id


@pytest.mark.django_db
def test_admin_can_delete_employee_and_linked_user(admin_client):
    nickname = f'del-{uuid4().hex[:8]}'
    admin_client.post(
        EMPLOYEES_URL,
        {
            'last_name': 'Delete',
            'first_name': 'Me',
            'nickname': nickname,
            'password': 'password123',
        },
        format='json',
    )
    employee = Employee.objects.get(nickname=nickname)
    user_id = employee.user_id
    response = admin_client.delete(employee_detail_url(employee.pk))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Employee.objects.filter(pk=employee.pk).exists()
    assert not User.objects.filter(pk=user_id).exists()


@pytest.mark.django_db
def test_work_rules_list_returns_all_without_pagination(auth_client):
    rule = _create_work_rule()
    response = auth_client.get(WORK_RULES_URL)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    codes = {item['code'] for item in response.data}
    assert rule.code in codes


@pytest.mark.django_db
def test_schedule_grid_requires_authentication(api_client):
    response = api_client.get(GRID_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_schedule_grid_returns_weeks_for_authenticated_user(auth_client, grid_setup):
    response = auth_client.get(GRID_URL, {'start': grid_setup['start_date'].isoformat()})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['start_date'] == grid_setup['start_date'].isoformat()
    assert len(response.data['weeks']) == response.data['weeks_count']
    first_cell = response.data['weeks'][0]['rows'][0]['cells'][0]
    assert first_cell['employee_id'] == grid_setup['employee'].id


@pytest.mark.django_db
def test_schedule_grid_history_requires_before_param(auth_client):
    response = auth_client.get(GRID_HISTORY_URL)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'before' in response.data['detail']


@pytest.mark.django_db
def test_schedule_grid_history_returns_past_weeks(auth_client, grid_setup):
    before_date = grid_setup['start_date'] + timedelta(days=7)
    response = auth_client.get(
        GRID_HISTORY_URL,
        {'before': before_date.isoformat(), 'weeks': 1},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['before_date'] == before_date.isoformat()
    assert response.data['weeks_count'] == 1
    history_cell = response.data['weeks'][0]['rows'][0]['cells'][0]
    assert history_cell['employee_id'] == grid_setup['employee'].id


@pytest.mark.django_db
def test_schedule_generate_forbidden_for_regular_user(auth_client):
    response = auth_client.post(GENERATE_URL, {'start': '2025-06-09'}, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_generate_schedule(admin_client, generate_setup):
    start_date = generate_setup['start_date']
    response = admin_client.post(
        GENERATE_URL,
        {'start': start_date.isoformat()},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['created_shifts'] == DAYS_IN_GRID
    assert response.data['grid']['start_date'] == start_date.isoformat()
    assert ScheduleShift.objects.count() == DAYS_IN_GRID


@pytest.mark.django_db
def test_schedule_bulk_save_forbidden_for_regular_user(auth_client, schedule_setup):
    response = auth_client.post(
        GRID_SAVE_URL,
        {
            'changes': [
                {
                    'date': schedule_setup['shift_date'].isoformat(),
                    'location_id': str(schedule_setup['location'].id),
                    'employee_id': str(schedule_setup['employee'].id),
                }
            ]
        },
        format='json',
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_bulk_save_schedule_changes(admin_client, schedule_setup):
    response = admin_client.post(
        GRID_SAVE_URL,
        {
            'changes': [
                {
                    'date': schedule_setup['shift_date'].isoformat(),
                    'location_id': str(schedule_setup['location'].id),
                    'employee_id': str(schedule_setup['employee'].id),
                }
            ]
        },
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['saved'] == 1
    shift = ScheduleShift.objects.get(
        date=schedule_setup['shift_date'],
        location=schedule_setup['location'],
    )
    assert shift.employee_id == schedule_setup['employee'].id
    assert 'grid' in response.data
