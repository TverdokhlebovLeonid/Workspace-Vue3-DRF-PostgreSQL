import pytest
from rest_framework.test import APIClient

from apps.users.models import User, UserRole


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='user',
        password='password123',
        role=UserRole.USER,
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username='admin',
        password='password123',
        role=UserRole.ADMIN,
    )


@pytest.fixture
def inactive_admin(db):
    return User.objects.create_user(
        username='inactive_admin',
        password='password123',
        role=UserRole.ADMIN,
        is_active=False,
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client
