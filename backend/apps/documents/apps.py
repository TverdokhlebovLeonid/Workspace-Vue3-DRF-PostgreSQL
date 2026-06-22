from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.documents'
    verbose_name = 'documents'

    def ready(self) -> None:
        from apps.documents import signals  # noqa: F401
