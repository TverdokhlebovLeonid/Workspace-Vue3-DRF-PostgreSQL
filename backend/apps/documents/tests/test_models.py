import pytest
from django.core.exceptions import ValidationError

from apps.documents.models import validate_document_image


class DummyUploadedFile:
    def __init__(self, name: str):
        self.name = name


@pytest.mark.parametrize('filename', ['report.png', 'photo.jpg', 'scan.jpeg'])
def test_validate_document_image_accepts_allowed_extensions(filename):
    validate_document_image(DummyUploadedFile(filename))


@pytest.mark.parametrize('filename', ['report.pdf', 'notes.txt', 'archive.zip'])
def test_validate_document_image_rejects_other_extensions(filename):
    with pytest.raises(ValidationError, match='Only PNG and JPG are allowed'):
        validate_document_image(DummyUploadedFile(filename))
