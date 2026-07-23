from uuid import uuid4

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.documents.models import Document, DocumentAccess
from apps.documents.tests.image_helpers import make_png_bytes, uploaded_png
from apps.schedules.models import Employee
from apps.schedules.services.employee_users import create_employee_with_user
from apps.users.models import User

DOCUMENTS_URL = reverse('documents-list')


def document_detail_url(document_id):
    return reverse('documents-detail', args=[document_id])


def document_access_url(document_id):
    return reverse('documents-access', args=[document_id])


def document_download_url(document_id):
    return reverse('documents-download', args=[document_id])


def _create_document(*, title: str = 'Manual') -> Document:
    return Document.objects.create(title=title, file=uploaded_png('folder/manual.png'))


def _create_employee(nickname: str | None = None) -> Employee:
    return Employee.objects.create(
        last_name='Test',
        first_name='User',
        nickname=nickname or f'emp-{uuid4().hex[:8]}',
    )


def _create_employee_user(**overrides) -> tuple[Employee, User]:
    nickname = overrides.pop('nickname', f'emp-{uuid4().hex[:8]}')
    data = {
        'last_name': 'Doc',
        'first_name': 'User',
        'nickname': nickname,
        'email': f'{nickname}@example.com',
        'is_active': True,
    }
    data.update(overrides)
    employee = create_employee_with_user(
        employee_data=data,
        password='password123',
        locations=[],
        work_rules=[],
    )
    return employee, employee.user


def _employee_client(employee_user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=employee_user)
    return client


@pytest.fixture
def media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.mark.django_db
def test_documents_list_requires_authentication(api_client):
    response = api_client.get(DOCUMENTS_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_documents_list_empty_for_user_without_employee_profile(auth_client):
    _create_document()
    response = auth_client.get(DOCUMENTS_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['results'] == []


@pytest.mark.django_db
def test_documents_list_shows_only_accessible_docs_for_employee_user():
    visible = _create_document(title='Visible')
    _create_document(title='Hidden')
    employee, user = _create_employee_user()
    DocumentAccess.objects.create(document=visible, employee=employee)
    response = _employee_client(user).get(DOCUMENTS_URL)
    assert response.status_code == status.HTTP_200_OK
    titles = {item['title'] for item in response.data['results']}
    assert titles == {'Visible'}


@pytest.mark.django_db
def test_documents_list_shows_all_for_admin_with_access_info(admin_client, admin_user):
    employee = _create_employee()
    document = _create_document()
    DocumentAccess.objects.create(document=document, employee=employee, granted_by=admin_user)
    response = admin_client.get(DOCUMENTS_URL)
    assert response.status_code == status.HTTP_200_OK
    item = response.data['results'][0]
    assert item['title'] == document.title
    assert item['employee_ids'] == [employee.id]
    assert len(item['access_entries']) == 1


@pytest.mark.django_db
def test_documents_upload_forbidden_for_regular_user(auth_client, media_root):
    response = auth_client.post(
        DOCUMENTS_URL,
        {'title': 'Secret', 'file': uploaded_png('upload.png')},
        format='multipart',
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Document.objects.count() == 0


@pytest.mark.django_db
def test_admin_can_upload_document(admin_client, admin_user, media_root):
    response = admin_client.post(
        DOCUMENTS_URL,
        {'title': 'Uploaded', 'file': uploaded_png('upload.png')},
        format='multipart',
    )
    assert response.status_code == status.HTTP_201_CREATED
    document = Document.objects.get(title='Uploaded')
    assert document.uploaded_by_id == admin_user.id
    assert document.file.name.endswith('.png')


@pytest.mark.django_db
def test_documents_delete_forbidden_for_regular_user(auth_client, media_root):
    document = _create_document()
    response = auth_client.delete(document_detail_url(document.pk))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Document.objects.filter(pk=document.pk).exists()


@pytest.mark.django_db
def test_admin_can_delete_document(admin_client, media_root):
    document = _create_document()
    response = admin_client.delete(document_detail_url(document.pk))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Document.objects.filter(pk=document.pk).exists()


@pytest.mark.django_db
def test_documents_access_update_forbidden_for_regular_user(auth_client, media_root):
    document = _create_document()
    employee = _create_employee()
    response = auth_client.patch(
        document_access_url(document.pk),
        {'employee_ids': [str(employee.id)]},
        format='json',
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert DocumentAccess.objects.filter(document=document).count() == 0


@pytest.mark.django_db
def test_admin_can_update_document_access(admin_client, media_root):
    document = _create_document()
    employee = _create_employee()
    response = admin_client.patch(
        document_access_url(document.pk),
        {'employee_ids': [str(employee.id)]},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['employee_ids'] == [employee.id]
    assert DocumentAccess.objects.filter(document=document, employee=employee).exists()


@pytest.mark.django_db
def test_documents_download_requires_authentication(api_client, media_root):
    document = _create_document()
    response = api_client.get(document_download_url(document.pk))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_documents_download_forbidden_without_access(media_root):
    document = _create_document()
    _, user = _create_employee_user()
    response = _employee_client(user).get(document_download_url(document.pk))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == 'Access denied.'


@pytest.mark.django_db
def test_employee_can_download_with_access(media_root):
    document = _create_document()
    employee, user = _create_employee_user()
    DocumentAccess.objects.create(document=document, employee=employee)
    response = _employee_client(user).get(document_download_url(document.pk))
    assert response.status_code == status.HTTP_200_OK
    content = b''.join(response.streaming_content)
    assert content.startswith(b'\x89PNG')


@pytest.mark.django_db
def test_admin_upload_rejects_non_image_content(admin_client, media_root):
    fake = SimpleUploadedFile('fake.png', b'not-an-image', content_type='image/png')
    response = admin_client.post(
        DOCUMENTS_URL,
        {'title': 'Bad', 'file': fake},
        format='multipart',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Document.objects.count() == 0


@pytest.mark.django_db
def test_admin_upload_rejects_oversized_image(admin_client, media_root, settings):
    settings.DOCUMENT_MAX_UPLOAD_BYTES = 100
    oversized = SimpleUploadedFile(
        'big.png',
        make_png_bytes((200, 200)),
        content_type='image/png',
    )
    response = admin_client.post(
        DOCUMENTS_URL,
        {'title': 'Big', 'file': oversized},
        format='multipart',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Document.objects.count() == 0


@pytest.mark.django_db
def test_admin_can_download_any_document(admin_client, media_root):
    document = _create_document()
    response = admin_client.get(document_download_url(document.pk))
    assert response.status_code == status.HTTP_200_OK
    assert 'attachment' in response['Content-Disposition']


@pytest.mark.django_db
def test_employee_list_marks_can_download_when_access_granted():
    document = _create_document()
    employee, user = _create_employee_user()
    DocumentAccess.objects.create(document=document, employee=employee)
    response = _employee_client(user).get(DOCUMENTS_URL)
    assert response.status_code == status.HTTP_200_OK
    item = response.data['results'][0]
    assert item['can_download'] is True
    assert item['employee_ids'] == []
