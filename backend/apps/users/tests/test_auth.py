import pytest
from django.urls import reverse
from rest_framework import status

from apps.users.auth_cookies import REFRESH_COOKIE_NAME

JWT_CREATE_URL = reverse('jwt-create')
JWT_REFRESH_URL = reverse('jwt-refresh')
LOGOUT_URL = reverse('logout')


@pytest.mark.django_db
def test_login_sets_http_only_refresh_cookie_without_body_refresh(api_client, user):
    response = api_client.post(
        JWT_CREATE_URL,
        {'username': user.username, 'password': 'password123'},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' not in response.data
    assert REFRESH_COOKIE_NAME in response.cookies
    cookie = response.cookies[REFRESH_COOKIE_NAME]
    assert cookie['httponly']
    assert cookie['path'] == '/api/auth/'


@pytest.mark.django_db
def test_refresh_uses_cookie_and_rotates_it(api_client, user):
    login = api_client.post(
        JWT_CREATE_URL,
        {'username': user.username, 'password': 'password123'},
        format='json',
    )
    api_client.cookies[REFRESH_COOKIE_NAME] = login.cookies[REFRESH_COOKIE_NAME].value
    response = api_client.post(JWT_REFRESH_URL, {}, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' not in response.data
    assert REFRESH_COOKIE_NAME in response.cookies


@pytest.mark.django_db
def test_refresh_without_cookie_returns_401(api_client):
    response = api_client.post(JWT_REFRESH_URL, {}, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_clears_refresh_cookie(api_client, user):
    login = api_client.post(
        JWT_CREATE_URL,
        {'username': user.username, 'password': 'password123'},
        format='json',
    )
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}')
    api_client.cookies[REFRESH_COOKIE_NAME] = login.cookies[REFRESH_COOKIE_NAME].value
    response = api_client.post(LOGOUT_URL, {}, format='json')
    assert response.status_code == status.HTTP_200_OK
    cleared = response.cookies[REFRESH_COOKIE_NAME]
    assert cleared.value == ''
    assert cleared['path'] == '/api/auth/'


@pytest.mark.django_db
def test_logout_clear_cookie_uses_secure_flag_in_production(settings, api_client, user):
    settings.DEBUG = False
    settings.JWT_AUTH_COOKIE_SECURE = True
    login = api_client.post(
        JWT_CREATE_URL,
        {'username': user.username, 'password': 'password123'},
        format='json',
    )
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}')
    api_client.cookies[REFRESH_COOKIE_NAME] = login.cookies[REFRESH_COOKIE_NAME].value
    response = api_client.post(LOGOUT_URL, {}, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.cookies[REFRESH_COOKIE_NAME]['secure']
