from datetime import date
from uuid import uuid4

import pytest

from apps.schedules.models import Employee, Location, LocationType, RuleKind, WorkRule, WorkRuleCode
from apps.schedules.serializers import (
    EmployeeSerializer,
    LocationSerializer,
    ScheduleBulkSaveSerializer,
)
from apps.schedules.services.employee_users import create_employee_with_user
from apps.users.models import User


def _create_location(**overrides) -> Location:
    data = {
        'name': f'loc-{uuid4().hex[:6]}',
        'location_type': LocationType.STORE,
        'is_active': True,
        'sort_order': 0,
    }
    data.update(overrides)
    return Location.objects.create(**data)


def _create_work_rule() -> WorkRule:
    return WorkRule.objects.create(
        code=WorkRuleCode.WORK_2_ON_2,
        name='2/2',
        kind=RuleKind.CYCLE,
    )


def _employee_payload(**overrides) -> dict:
    data = {
        'last_name': 'Ivanov',
        'first_name': 'Ivan',
        'nickname': f'nick-{uuid4().hex[:8]}',
        'email': 'employee@example.com',
        'phone': '+79990000000',
        'is_active': True,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_location_serializer_returns_type_label():
    location = _create_location(location_type=LocationType.CASH_REGISTER)
    data = LocationSerializer(location).data
    assert data['location_type'] == LocationType.CASH_REGISTER
    assert data['location_type_label'] == 'Cash register'


@pytest.mark.django_db
def test_location_serializer_creates_location():
    serializer = LocationSerializer(
        data={
            'location_type': LocationType.STORE,
            'name': 'Main store',
            'is_active': True,
            'sort_order': 5,
        }
    )
    assert serializer.is_valid(), serializer.errors
    location = serializer.save()
    assert location.name == 'Main store'
    assert location.sort_order == 5


@pytest.mark.django_db
def test_location_serializer_updates_location():
    location = _create_location(name='Old name')
    serializer = LocationSerializer(
        location,
        data={'name': 'New name', 'is_active': False},
        partial=True,
    )
    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()
    assert updated.name == 'New name'
    assert updated.is_active is False


@pytest.mark.django_db
def test_employee_serializer_creates_with_password_and_relations():
    location = _create_location()
    work_rule = _create_work_rule()
    payload = _employee_payload(
        location_ids=[location.id],
        work_rule_ids=[work_rule.id],
        password='password123',
    )
    serializer = EmployeeSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors
    employee = serializer.save()
    user = User.objects.get(username=payload['nickname'])
    assert employee.user_id == user.id
    assert list(employee.locations.all()) == [location]
    assert list(employee.work_rules.all()) == [work_rule]


@pytest.mark.django_db
def test_employee_serializer_rejects_create_without_password():
    serializer = EmployeeSerializer(data=_employee_payload())
    assert serializer.is_valid() is False
    assert 'password' in serializer.errors


@pytest.mark.django_db
def test_employee_serializer_rejects_short_password():
    serializer = EmployeeSerializer(data=_employee_payload(password='short'))
    assert serializer.is_valid() is False
    assert 'password' in serializer.errors


@pytest.mark.django_db
def test_employee_serializer_has_user_false_without_linked_user():
    employee = Employee.objects.create(
        last_name='Solo',
        first_name='Worker',
        nickname='solo-worker',
    )
    data = EmployeeSerializer(employee).data
    assert data['has_user'] is False


@pytest.mark.django_db
def test_employee_serializer_has_user_true_with_linked_user():
    employee = create_employee_with_user(
        employee_data=_employee_payload(),
        password='password123',
        locations=[],
        work_rules=[],
    )
    data = EmployeeSerializer(employee).data
    assert data['has_user'] is True


@pytest.mark.django_db
def test_employee_serializer_read_nested_locations_and_rules():
    location = _create_location()
    work_rule = _create_work_rule()
    employee = create_employee_with_user(
        employee_data=_employee_payload(),
        password='password123',
        locations=[location],
        work_rules=[work_rule],
    )
    data = EmployeeSerializer(employee).data
    assert data['location_ids'] == [location.id]
    assert data['work_rule_ids'] == [work_rule.id]
    assert data['locations'][0]['name'] == location.name
    assert data['work_rules'][0]['code'] == work_rule.code


@pytest.mark.django_db
def test_employee_serializer_update_without_password():
    employee = create_employee_with_user(
        employee_data=_employee_payload(nickname='old-nick'),
        password='password123',
        locations=[],
        work_rules=[],
    )
    serializer = EmployeeSerializer(
        employee,
        data={'first_name': 'Petr', 'last_name': 'Petrov'},
        partial=True,
    )
    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()
    assert updated.first_name == 'Petr'
    assert updated.last_name == 'Petrov'


@pytest.mark.django_db
def test_employee_serializer_location_ids_excludes_inactive_locations():
    inactive_location = _create_location(is_active=False)
    serializer = EmployeeSerializer(
        data=_employee_payload(
            location_ids=[inactive_location.id],
            password='password123',
        )
    )
    assert serializer.is_valid() is False
    assert 'location_ids' in serializer.errors


@pytest.mark.django_db
def test_schedule_bulk_save_accepts_valid_changes():
    location_id = uuid4()
    employee_id = uuid4()
    serializer = ScheduleBulkSaveSerializer(
        data={
            'changes': [
                {
                    'date': '2025-06-10',
                    'location_id': str(location_id),
                    'employee_id': str(employee_id),
                }
            ]
        }
    )
    assert serializer.is_valid(), serializer.errors
    change = serializer.validated_data['changes'][0]
    assert change['date'] == date(2025, 6, 10)
    assert change['location_id'] == location_id
    assert change['employee_id'] == employee_id


@pytest.mark.django_db
def test_schedule_bulk_save_rejects_empty_changes():
    serializer = ScheduleBulkSaveSerializer(data={'changes': []})
    assert serializer.is_valid() is False
    assert 'changes' in serializer.errors


@pytest.mark.django_db
def test_schedule_bulk_save_accepts_null_employee_id():
    location_id = uuid4()
    serializer = ScheduleBulkSaveSerializer(
        data={
            'changes': [
                {
                    'date': '2025-06-10',
                    'location_id': str(location_id),
                    'employee_id': None,
                }
            ]
        }
    )
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['changes'][0]['employee_id'] is None


@pytest.mark.django_db
def test_schedule_bulk_save_rejects_invalid_uuid():
    serializer = ScheduleBulkSaveSerializer(
        data={
            'changes': [
                {
                    'date': '2025-06-10',
                    'location_id': 'not-a-uuid',
                    'employee_id': None,
                }
            ]
        }
    )
    assert serializer.is_valid() is False
    assert 'changes' in serializer.errors
