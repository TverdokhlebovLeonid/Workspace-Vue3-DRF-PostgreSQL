from uuid import uuid4

import pytest
from rest_framework.test import APIRequestFactory

from apps.documents.models import Document, DocumentAccess
from apps.documents.serializers import (
    DocumentAccessUpdateSerializer,
    DocumentSerializer,
    DocumentUploadSerializer,
)
from apps.documents.tests.image_helpers import uploaded_png
from apps.schedules.models import Employee

factory = APIRequestFactory()


def _create_document(*, title: str = 'Manual') -> Document:
    return Document.objects.create(title=title, file=uploaded_png('folder/manual.png'))


def _create_employee(nickname: str | None = None) -> Employee:
    return Employee.objects.create(
        last_name='Test',
        first_name='User',
        nickname=nickname or f'emp-{uuid4().hex[:8]}',
    )


@pytest.mark.django_db
def test_document_serializer_returns_file_name():
    document = _create_document()
    data = DocumentSerializer(document).data
    assert data['file_name'] == document.file.name.split('/')[-1]


@pytest.mark.django_db
def test_document_serializer_allows_download_for_admin(admin_user):
    document = _create_document()
    data = DocumentSerializer(document, context={'is_admin': True}).data
    assert data['can_download'] is True


@pytest.mark.django_db
def test_document_serializer_uses_download_map_for_user(user):
    document = _create_document()
    allowed = DocumentSerializer(
        document,
        context={'can_download_map': {document.pk: True}},
    ).data
    denied = DocumentSerializer(document, context={'can_download_map': {}}).data
    assert allowed['can_download'] is True
    assert denied['can_download'] is False


@pytest.mark.django_db
def test_document_serializer_hides_access_without_include_access_flag(admin_user):
    employee = _create_employee()
    document = _create_document()
    DocumentAccess.objects.create(document=document, employee=employee, granted_by=admin_user)
    data = DocumentSerializer(document).data
    assert data['employee_ids'] == []
    assert data['access_entries'] == []


@pytest.mark.django_db
def test_document_serializer_exposes_access_with_include_access_flag(admin_user):
    employee = _create_employee()
    document = _create_document()
    DocumentAccess.objects.create(document=document, employee=employee, granted_by=admin_user)
    data = DocumentSerializer(
        document,
        context={'include_access': True},
    ).data
    assert data['employee_ids'] == [employee.id]
    assert len(data['access_entries']) == 1
    assert data['access_entries'][0]['employee_id'] == str(employee.id)
    assert data['access_entries'][0]['granted_by_username'] == admin_user.username


@pytest.mark.django_db
def test_document_upload_serializer_sets_uploaded_by(admin_user):
    request = factory.post('/')
    request.user = admin_user
    serializer = DocumentUploadSerializer(
        data={'title': 'Uploaded', 'file': uploaded_png('upload.png')},
        context={'request': request},
    )
    assert serializer.is_valid(), serializer.errors
    document = serializer.save()
    assert document.uploaded_by_id == admin_user.id
    assert document.title == 'Uploaded'


@pytest.mark.django_db
def test_document_access_update_rejects_unknown_employee_ids():
    document = _create_document()
    request = factory.post('/')
    serializer = DocumentAccessUpdateSerializer(
        data={'employee_ids': [str(uuid4())]},
        context={'request': request},
    )
    assert serializer.is_valid() is False
    assert 'employee_ids' in serializer.errors


@pytest.mark.django_db
def test_document_access_update_syncs_access_entries(admin_user):
    document = _create_document()
    first_employee = _create_employee()
    second_employee = _create_employee()
    DocumentAccess.objects.create(
        document=document,
        employee=first_employee,
        granted_by=admin_user,
    )
    request = factory.post('/')
    request.user = admin_user
    serializer = DocumentAccessUpdateSerializer(
        data={'employee_ids': [str(second_employee.id)]},
        context={'request': request},
    )
    assert serializer.is_valid(), serializer.errors
    serializer.save(document)
    employee_ids = set(
        DocumentAccess.objects.filter(document=document).values_list('employee_id', flat=True)
    )
    assert employee_ids == {second_employee.id}


@pytest.mark.django_db
def test_document_access_update_allows_clearing_all_access(admin_user):
    document = _create_document()
    employee = _create_employee()
    DocumentAccess.objects.create(document=document, employee=employee, granted_by=admin_user)
    request = factory.post('/')
    request.user = admin_user
    serializer = DocumentAccessUpdateSerializer(
        data={'employee_ids': []},
        context={'request': request},
    )
    assert serializer.is_valid(), serializer.errors
    serializer.save(document)
    assert DocumentAccess.objects.filter(document=document).count() == 0
