import pytest

from apps.users.models import User, UserLanguage, UserRole


@pytest.mark.django_db
def test_is_admin_for_admin_role(admin_user):
    assert admin_user.is_admin is True


@pytest.mark.django_db
def test_is_admin_for_user_role(user):
    assert user.is_admin is False


@pytest.mark.django_db
def test_default_role_and_language():
    created = User.objects.create_user(username='defaults', password='password123')
    assert created.role == UserRole.USER
    assert created.language == UserLanguage.EN


@pytest.mark.django_db
def test_str_returns_username(user):
    assert str(user) == 'user'
