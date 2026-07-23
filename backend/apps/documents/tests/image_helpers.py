from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def make_png_bytes(size: tuple[int, int] = (1, 1)) -> bytes:
    buffer = BytesIO()
    Image.new('RGB', size, color=(255, 0, 0)).save(buffer, format='PNG')
    return buffer.getvalue()


def uploaded_png(name: str = 'scan.png') -> SimpleUploadedFile:
    return SimpleUploadedFile(name, make_png_bytes(), content_type='image/png')
