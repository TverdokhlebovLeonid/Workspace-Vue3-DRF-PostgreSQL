import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.documents.models import validate_document_image
from apps.documents.tests.image_helpers import make_png_bytes, uploaded_png


@pytest.mark.parametrize('filename', ['report.png', 'photo.jpg', 'scan.jpeg'])
def test_validate_document_image_accepts_allowed_extensions(filename):
    validate_document_image(uploaded_png(filename))


@pytest.mark.parametrize('filename', ['report.pdf', 'notes.txt', 'archive.zip'])
def test_validate_document_image_rejects_other_extensions(filename):
    with pytest.raises(ValidationError, match='Only PNG and JPG are allowed'):
        validate_document_image(SimpleUploadedFile(filename, b'data'))


def test_validate_document_image_rejects_fake_png_content():
    fake = SimpleUploadedFile('fake.png', b'not-an-image', content_type='image/png')
    with pytest.raises(ValidationError, match='Invalid image file'):
        validate_document_image(fake)


def test_validate_document_image_rejects_oversized_file(settings):
    settings.DOCUMENT_MAX_UPLOAD_BYTES = 50
    oversized = SimpleUploadedFile(
        'big.png',
        make_png_bytes((80, 80)),
        content_type='image/png',
    )
    with pytest.raises(ValidationError, match='too large'):
        validate_document_image(oversized)
