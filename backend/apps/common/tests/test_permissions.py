import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory

from apps.common.permissions import IsAdminRole, IsAuthenticatedReadOnly

factory = APIRequestFactory()


def _request(method: str, user):
    request = getattr(factory, method.lower())('/')
    request.user = user
    return request


@pytest.mark.parametrize(
    ('user_factory', 'expected'),
    [
        ('admin_user', True),
        ('user', False),
        ('inactive_admin', False),
    ],
)
def test_is_admin_role(request, user_factory, expected):
    user = request.getfixturevalue(user_factory)
    assert IsAdminRole().has_permission(_request('GET', user), None) is expected


def test_is_admin_role_anonymous():
    assert IsAdminRole().has_permission(_request('GET', AnonymousUser()), None) is False


@pytest.mark.parametrize(
    ('method', 'user_factory', 'expected'),
    [
        ('GET', 'user', True),
        ('HEAD', 'user', True),
        ('OPTIONS', 'user', True),
        ('POST', 'user', False),
        ('PATCH', 'user', False),
        ('POST', 'admin_user', True),
    ],
)
def test_is_authenticated_read_only(request, method, user_factory, expected):
    user = request.getfixturevalue(user_factory)
    assert IsAuthenticatedReadOnly().has_permission(_request(method, user), None) is expected


def test_is_authenticated_read_only_anonymous():
    assert (
        IsAuthenticatedReadOnly().has_permission(_request('GET', AnonymousUser()), None) is False
    )
