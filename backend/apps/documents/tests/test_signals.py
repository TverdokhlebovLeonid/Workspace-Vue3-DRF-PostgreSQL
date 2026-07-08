import os

import pytest
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.documents.models import Document
from apps.documents.signals import delete_document_file


def _uploaded_file(name: str = 'scan.png') -> SimpleUploadedFile:
    return SimpleUploadedFile(name, b'image-content', content_type='image/png')


def _create_document(*, title: str = 'Manual', filename: str = 'folder/manual.png') -> Document:
    return Document.objects.create(title=title, file=_uploaded_file(filename))


@pytest.mark.django_db
def test_deleting_document_removes_file_from_storage(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    document = _create_document()
    stored_name = document.file.name
    storage_path = document.file.path
    assert os.path.exists(storage_path)
    document.delete()
    assert not default_storage.exists(stored_name)
    assert not os.path.exists(storage_path)


@pytest.mark.django_db
def test_delete_document_file_noop_without_file():
    document = Document(title='Without file')
    delete_document_file(Document, document)


@pytest.mark.django_db
def test_deleting_document_does_not_remove_other_files(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    first = _create_document(title='First', filename='first.png')
    second = _create_document(title='Second', filename='second.png')
    second_name = second.file.name
    second_path = second.file.path
    first.delete()
    assert default_storage.exists(second_name)
    assert os.path.exists(second_path)
