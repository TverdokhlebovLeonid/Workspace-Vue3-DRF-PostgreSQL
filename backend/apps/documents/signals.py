from django.db.models.signals import post_delete
from django.dispatch import receiver

from apps.documents.models import Document


@receiver(post_delete, sender=Document)
def delete_document_file(sender, instance: Document, **kwargs) -> None:
    if instance.file:
        instance.file.delete(save=False)
