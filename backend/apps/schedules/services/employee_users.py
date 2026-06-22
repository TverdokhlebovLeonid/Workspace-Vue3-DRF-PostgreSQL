from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.schedules.models import Employee
from apps.users.models import User, UserRole


def _user_fields(employee_data: dict) -> dict:
    return {
        'email': employee_data.get('email') or '',
        'first_name': employee_data.get('first_name', ''),
        'last_name': employee_data.get('last_name', ''),
    }


def create_employee_with_user(
    *, employee_data: dict, password: str, locations, work_rules
) -> Employee:
    nickname = employee_data['nickname']
    if User.objects.filter(username=nickname).exists():
        raise ValidationError({'nickname': 'A user with this username already exists.'})
    if Employee.objects.filter(nickname=nickname).exists():
        raise ValidationError({'nickname': 'An employee with this nickname already exists.'})
    with transaction.atomic():
        user = User.objects.create_user(
            username=nickname,
            password=password,
            role=UserRole.USER,
            **_user_fields(employee_data),
        )
        employee = Employee.objects.create(user=user, **employee_data)
        employee.locations.set(locations)
        employee.work_rules.set(work_rules)
    return employee


def update_employee_user(
    employee: Employee, *, employee_data: dict, password: str | None, locations, work_rules
) -> Employee:
    new_nickname = employee_data.get('nickname', employee.nickname)
    with transaction.atomic():
        if employee.user_id:
            user = employee.user
            if User.objects.exclude(pk=user.pk).filter(username=new_nickname).exists():
                raise ValidationError({'nickname': 'A user with this username already exists.'})
            user.username = new_nickname
            for field, value in _user_fields(employee_data).items():
                setattr(user, field, value)
            user.is_active = employee_data.get('is_active', True)
            if password:
                user.set_password(password)
            user.save()
        elif password:
            if User.objects.filter(username=new_nickname).exists():
                raise ValidationError({'nickname': 'A user with this username already exists.'})
            user = User.objects.create_user(
                username=new_nickname,
                password=password,
                role=UserRole.USER,
                **_user_fields(employee_data),
            )
            employee.user = user
        for field, value in employee_data.items():
            setattr(employee, field, value)
        employee.save()
        employee.locations.set(locations)
        employee.work_rules.set(work_rules)
    return employee


def delete_employee_user(employee: Employee) -> None:
    user = employee.user
    employee.delete()
    if user and user.role == UserRole.USER:
        user.delete()
