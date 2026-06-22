import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import UUIDModel


def validate_document_image(file) -> None:
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ('.png', '.jpg', '.jpeg'):
        raise ValidationError('Only PNG and JPG are allowed.')


class Document(UUIDModel):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/%Y/%m/', validators=[validate_document_image])
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'document'
        verbose_name_plural = 'documents'

    def __str__(self) -> str:
        return self.title


class DocumentAccess(UUIDModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='access_entries')
    employee = models.ForeignKey(
        'schedules.Employee', on_delete=models.CASCADE, related_name='document_access_entries'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_document_access',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['document', 'employee'], name='unique_document_employee'
            )
        ]
        verbose_name = 'document access'
        verbose_name_plural = 'document access entries'

    def __str__(self) -> str:
        return f'{self.document} → {self.employee}'
