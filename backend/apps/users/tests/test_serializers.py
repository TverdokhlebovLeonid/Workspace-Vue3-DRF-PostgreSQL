import pytest
from rest_framework.test import APIRequestFactory

from apps.users.models import User, UserLanguage, UserRole
from apps.users.serializers import (
    ChangePasswordSerializer,
    UserCreateSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
)

factory = APIRequestFactory()


@pytest.mark.django_db
def test_user_profile_update_accepts_supported_language(user):
    serializer = UserProfileUpdateSerializer(
        user,
        data={'language': UserLanguage.RU},
        partial=True,
    )
    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()
    assert updated.language == UserLanguage.RU


@pytest.mark.django_db
def test_user_profile_update_rejects_invalid_language(user):
    serializer = UserProfileUpdateSerializer(
        user,
        data={'language': 'de'},
        partial=True,
    )
    assert serializer.is_valid() is False
    assert 'language' in serializer.errors


@pytest.mark.django_db
def test_change_password_success(user):
    request = factory.post('/')
    request.user = user
    serializer = ChangePasswordSerializer(
        data={'current_password': 'password123', 'new_password': 'newpassword1'},
        context={'request': request},
    )
    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_change_password_rejects_wrong_current_password(user):
    request = factory.post('/')
    request.user = user
    serializer = ChangePasswordSerializer(
        data={'current_password': 'wrong-password', 'new_password': 'newpassword1'},
        context={'request': request},
    )
    assert serializer.is_valid() is False
    assert serializer.errors['current_password'] == ['Incorrect current password.']


@pytest.mark.django_db
def test_change_password_rejects_short_new_password(user):
    request = factory.post('/')
    request.user = user
    serializer = ChangePasswordSerializer(
        data={'current_password': 'password123', 'new_password': 'short'},
        context={'request': request},
    )
    assert serializer.is_valid() is False
    assert 'new_password' in serializer.errors


@pytest.mark.django_db
def test_user_create_creates_regular_user():
    serializer = UserCreateSerializer(
        data={
            'username': 'new-user',
            'email': 'new@example.com',
            'password': 'password123',
        }
    )
    assert serializer.is_valid(), serializer.errors
    created = serializer.save()
    assert created.role == UserRole.USER
    assert created.is_staff is False
    assert created.check_password('password123')


@pytest.mark.django_db
def test_user_create_creates_admin_with_staff_flag():
    serializer = UserCreateSerializer(
        data={
            'username': 'new-admin',
            'email': 'admin@example.com',
            'password': 'password123',
            'role': UserRole.ADMIN,
        }
    )
    assert serializer.is_valid(), serializer.errors
    created = serializer.save()
    assert created.role == UserRole.ADMIN
    assert created.is_staff is True


@pytest.mark.django_db
def test_user_create_rejects_invalid_role():
    serializer = UserCreateSerializer(
        data={
            'username': 'bad-role',
            'email': 'bad@example.com',
            'password': 'password123',
            'role': 'SUPERUSER',
        }
    )
    assert serializer.is_valid() is False
    assert 'role' in serializer.errors


@pytest.mark.django_db
def test_user_create_rejects_short_password():
    serializer = UserCreateSerializer(
        data={
            'username': 'short-pass',
            'email': 'short@example.com',
            'password': 'short',
        }
    )
    assert serializer.is_valid() is False
    assert 'password' in serializer.errors


@pytest.mark.django_db
def test_user_serializer_output(user):
    data = UserSerializer(user).data
    assert data['username'] == 'user'
    assert data['role'] == UserRole.USER
    assert data['language'] == UserLanguage.EN
    assert set(data.keys()) == {
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'language',
    }


@pytest.mark.django_db
def test_user_serializer_fields_are_read_only(user):
    assert set(UserSerializer.Meta.read_only_fields) == set(UserSerializer.Meta.fields)
    serializer = UserSerializer(
        user,
        data={'username': 'hacked', 'role': UserRole.ADMIN},
        partial=True,
    )
    assert serializer.is_valid()
    serializer.save()
    user.refresh_from_db()
    assert user.username == 'user'
    assert user.role == UserRole.USER
