import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = ('ADMIN', 'Admin')
    USER = ('USER', 'User')


class UserLanguage(models.TextChoices):
    EN = ('en', 'English')
    RU = ('ru', 'Russian')


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.USER)
    language = models.CharField(max_length=5, choices=UserLanguage.choices, default=UserLanguage.EN)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['username']

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def __str__(self) -> str:
        return self.username
