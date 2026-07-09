from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status

from apps.users.models import User, UserLanguage, UserRole

ME_URL = reverse('me')
PASSWORD_URL = reverse('me-password')
USERS_URL = reverse('users')
HEALTH_URL = reverse('health')


def user_detail_url(user_id):
    return reverse('user-detail', args=[user_id])


@pytest.mark.django_db
def test_me_requires_authentication(api_client):
    response = api_client.get(ME_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_me_returns_current_user(auth_client, user):
    response = auth_client.get(ME_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == user.username
    assert response.data['role'] == UserRole.USER


@pytest.mark.django_db
def test_me_patch_updates_language(auth_client, user):
    response = auth_client.patch(ME_URL, {'language': UserLanguage.RU}, format='json')
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.language == UserLanguage.RU
    assert response.data['language'] == UserLanguage.RU


@pytest.mark.django_db
def test_change_password_success(auth_client, user):
    response = auth_client.post(
        PASSWORD_URL,
        {'current_password': 'password123', 'new_password': 'newpassword1'},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.check_password('newpassword1')


@pytest.mark.django_db
def test_change_password_rejects_wrong_current_password(auth_client):
    response = auth_client.post(
        PASSWORD_URL,
        {'current_password': 'wrong-password', 'new_password': 'newpassword1'},
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'current_password' in response.data


@pytest.mark.django_db
def test_users_list_forbidden_for_regular_user(auth_client):
    response = auth_client.get(USERS_URL)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_users_list_available_for_admin(admin_client, user, admin_user):
    response = admin_client.get(USERS_URL)
    assert response.status_code == status.HTTP_200_OK
    usernames = {item['username'] for item in response.data['results']}
    assert user.username in usernames
    assert admin_user.username in usernames


@pytest.mark.django_db
def test_admin_can_create_user(admin_client):
    response = admin_client.post(
        USERS_URL,
        {
            'username': 'created-user',
            'email': 'created@example.com',
            'password': 'password123',
            'role': UserRole.USER,
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED
    created = User.objects.get(username='created-user')
    assert created.role == UserRole.USER
    assert created.check_password('password123')


@pytest.mark.django_db
def test_admin_cannot_delete_own_account(admin_client, admin_user):
    response = admin_client.delete(user_detail_url(admin_user.pk))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert User.objects.filter(pk=admin_user.pk).exists()


@pytest.mark.django_db
def test_admin_cannot_delete_last_admin(admin_client, admin_user):
    other_admin = User.objects.create_user(
        username='other-admin',
        password='password123',
        role=UserRole.ADMIN,
    )
    with patch('apps.users.views.User.objects.filter') as mock_filter:
        mock_filter.return_value.count.return_value = 1
        response = admin_client.delete(user_detail_url(other_admin.pk))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert User.objects.filter(pk=other_admin.pk).exists()


@pytest.mark.django_db
def test_admin_can_delete_other_user(admin_client, user):
    response = admin_client.delete(user_detail_url(user.pk))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not User.objects.filter(pk=user.pk).exists()


@pytest.mark.django_db
def test_health_endpoint_ok(api_client):
    response = api_client.get(HEALTH_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {'status': 'ok', 'database': 'ok'}


@pytest.mark.django_db
def test_health_endpoint_reports_database_error(api_client):
    with patch('apps.users.views.connection.cursor', side_effect=Exception('db down')):
        response = api_client.get(HEALTH_URL)
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.data == {'status': 'error', 'database': 'unavailable'}
