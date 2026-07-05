from uuid import uuid4

import pytest
from rest_framework.exceptions import ValidationError

from apps.schedules.models import Employee, Location, RuleKind, WorkRule, WorkRuleCode
from apps.schedules.services.employee_users import (
    create_employee_with_user,
    delete_employee_user,
    update_employee_user,
)
from apps.users.models import User, UserRole


def _employee_data(**overrides) -> dict:
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


def _create_location() -> Location:
    return Location.objects.create(name=f'loc-{uuid4().hex[:6]}')


def _create_work_rule() -> WorkRule:
    return WorkRule.objects.create(
        code=WorkRuleCode.WORK_2_ON_2,
        name='2/2',
        kind=RuleKind.CYCLE,
    )


@pytest.mark.django_db
def test_create_employee_with_user_success():
    location = _create_location()
    work_rule = _create_work_rule()
    data = _employee_data()
    employee = create_employee_with_user(
        employee_data=data,
        password='password123',
        locations=[location],
        work_rules=[work_rule],
    )
    user = User.objects.get(username=data['nickname'])
    assert employee.user_id == user.id
    assert user.role == UserRole.USER
    assert user.email == data['email']
    assert user.check_password('password123')
    assert list(employee.locations.all()) == [location]
    assert list(employee.work_rules.all()) == [work_rule]


@pytest.mark.django_db
def test_create_employee_with_user_rejects_duplicate_username():
    data = _employee_data()
    User.objects.create_user(username=data['nickname'], password='password123')
    with pytest.raises(ValidationError, match='username already exists'):
        create_employee_with_user(
            employee_data=data,
            password='password123',
            locations=[],
            work_rules=[],
        )


@pytest.mark.django_db
def test_create_employee_with_user_rejects_duplicate_nickname():
    data = _employee_data()
    Employee.objects.create(
        last_name='Old',
        first_name='Old',
        nickname=data['nickname'],
    )
    with pytest.raises(ValidationError, match='nickname already exists'):
        create_employee_with_user(
            employee_data=data,
            password='password123',
            locations=[],
            work_rules=[],
        )


@pytest.mark.django_db
def test_update_employee_user_changes_profile_and_username():
    employee = create_employee_with_user(
        employee_data=_employee_data(nickname='old-nick'),
        password='password123',
        locations=[],
        work_rules=[],
    )
    updated = update_employee_user(
        employee,
        employee_data=_employee_data(
            nickname='new-nick',
            email='new@example.com',
            first_name='Petr',
            last_name='Petrov',
            is_active=True,
        ),
        password=None,
        locations=[],
        work_rules=[],
    )
    user = User.objects.get(pk=employee.user_id)
    assert updated.nickname == 'new-nick'
    assert user.username == 'new-nick'
    assert user.email == 'new@example.com'
    assert user.first_name == 'Petr'
    assert user.last_name == 'Petrov'


@pytest.mark.django_db
def test_update_employee_user_changes_password():
    employee = create_employee_with_user(
        employee_data=_employee_data(),
        password='password123',
        locations=[],
        work_rules=[],
    )
    update_employee_user(
        employee,
        employee_data=_employee_data(nickname=employee.nickname),
        password='newpassword1',
        locations=[],
        work_rules=[],
    )
    user = User.objects.get(pk=employee.user_id)
    assert user.check_password('newpassword1')


@pytest.mark.django_db
def test_update_employee_user_syncs_user_is_active():
    employee = create_employee_with_user(
        employee_data=_employee_data(is_active=True),
        password='password123',
        locations=[],
        work_rules=[],
    )
    update_employee_user(
        employee,
        employee_data=_employee_data(nickname=employee.nickname, is_active=False),
        password=None,
        locations=[],
        work_rules=[],
    )
    user = User.objects.get(pk=employee.user_id)
    assert user.is_active is False


@pytest.mark.django_db
def test_update_employee_user_updates_locations_and_rules():
    location = _create_location()
    work_rule = _create_work_rule()
    employee = create_employee_with_user(
        employee_data=_employee_data(),
        password='password123',
        locations=[],
        work_rules=[],
    )
    update_employee_user(
        employee,
        employee_data=_employee_data(nickname=employee.nickname),
        password=None,
        locations=[location],
        work_rules=[work_rule],
    )
    employee.refresh_from_db()
    assert list(employee.locations.all()) == [location]
    assert list(employee.work_rules.all()) == [work_rule]


@pytest.mark.django_db
def test_update_employee_user_rejects_duplicate_username():
    employee = create_employee_with_user(
        employee_data=_employee_data(nickname='employee-a'),
        password='password123',
        locations=[],
        work_rules=[],
    )
    User.objects.create_user(username='employee-b', password='password123')
    with pytest.raises(ValidationError, match='username already exists'):
        update_employee_user(
            employee,
            employee_data=_employee_data(nickname='employee-b'),
            password=None,
            locations=[],
            work_rules=[],
        )


@pytest.mark.django_db
def test_update_employee_user_creates_user_when_missing():
    employee = Employee.objects.create(
        last_name='Solo',
        first_name='Worker',
        nickname='solo-worker',
    )
    updated = update_employee_user(
        employee,
        employee_data=_employee_data(nickname='solo-worker'),
        password='password123',
        locations=[],
        work_rules=[],
    )
    user = User.objects.get(username='solo-worker')
    assert updated.user_id == user.id
    assert user.check_password('password123')


@pytest.mark.django_db
def test_delete_employee_user_removes_linked_user():
    employee = create_employee_with_user(
        employee_data=_employee_data(),
        password='password123',
        locations=[],
        work_rules=[],
    )
    user_id = employee.user_id
    delete_employee_user(employee)
    assert not Employee.objects.filter(pk=employee.pk).exists()
    assert not User.objects.filter(pk=user_id).exists()


@pytest.mark.django_db
def test_delete_employee_user_keeps_admin_user():
    admin = User.objects.create_user(
        username='admin-linked',
        password='password123',
        role=UserRole.ADMIN,
    )
    employee = Employee.objects.create(
        last_name='Boss',
        first_name='Admin',
        nickname='boss',
        user=admin,
    )
    delete_employee_user(employee)
    assert not Employee.objects.filter(pk=employee.pk).exists()
    assert User.objects.filter(pk=admin.pk).exists()
