import os

from django.core.management.base import BaseCommand, CommandError

from apps.users.models import User, UserRole


class Command(BaseCommand):
    help = (
        'Creates the first administrator from environment variables. '
        'Run manually once after migrate.'
    )

    def handle(self, *args, **options):
        username = os.getenv('BOOTSTRAP_ADMIN_USERNAME')
        email = os.getenv('BOOTSTRAP_ADMIN_EMAIL', '')
        password = os.getenv('BOOTSTRAP_ADMIN_PASSWORD')
        if not username or not password:
            raise CommandError(
                'Set BOOTSTRAP_ADMIN_USERNAME and BOOTSTRAP_ADMIN_PASSWORD in the environment.'
            )
        if User.objects.filter(role=UserRole.ADMIN).exists():
            self.stdout.write(
                self.style.WARNING('Administrator already exists — command made no changes.')
            )
            return
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=UserRole.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self.stdout.write(self.style.SUCCESS(f'Created administrator: {user.username}'))
