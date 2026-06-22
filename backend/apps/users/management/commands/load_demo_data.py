import json
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.schedules.models import Employee, Location, WorkRule
from apps.schedules.services.constants import DAYS_IN_GRID
from apps.schedules.services.employee_users import create_employee_with_user
from apps.schedules.services.generator import generate_schedule
from apps.schedules.services.period import resolve_grid_start
from apps.users.models import User, UserLanguage, UserRole


def demo_dataset_path() -> Path:
    return Path(settings.BASE_DIR) / 'fixtures' / 'demo' / 'dataset.json'


def load_dataset() -> dict:
    path = demo_dataset_path()
    if not path.is_file():
        raise CommandError(f'Demo dataset file not found: {path}')
    with path.open(encoding='utf-8') as handle:
        return json.load(handle)


class Command(BaseCommand):
    help = (
        'Loads demo data from fixtures/demo/dataset.json (locations, employees, admin, schedule).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear application data first (clear_app_data).',
        )
        parser.add_argument(
            '--skip-schedule', action='store_true', help='Do not generate schedule after loading.'
        )
        parser.add_argument(
            '--file',
            type=str,
            default='',
            help='Path to JSON file (default: fixtures/demo/dataset.json).',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            call_command('clear_app_data')
        dataset = load_dataset() if not options['file'] else self._load_file(options['file'])
        call_command('seed_work_rules')
        self._create_admin(dataset['admin'])
        location_map = self._create_locations(dataset.get('locations', []))
        self._create_employees(dataset.get('employees', []), location_map)
        if dataset.get('generate_schedule', True) and (not options['skip_schedule']):
            start = resolve_grid_start()
            created = generate_schedule(start, days=DAYS_IN_GRID)
            self.stdout.write(self.style.SUCCESS(f'Schedule generated: {created} shifts.'))
        self.stdout.write(self.style.SUCCESS('Demo data loaded.'))
        self.stdout.write(f'Admin: {dataset["admin"]["username"]} / {dataset["admin"]["password"]}')

    def _load_file(self, file_path: str) -> dict:
        path = Path(file_path)
        if not path.is_file():
            raise CommandError(f'File not found: {path}')
        with path.open(encoding='utf-8') as handle:
            return json.load(handle)

    def _create_admin(self, admin_data: dict) -> User:
        username = admin_data['username']
        password = admin_data['password']
        email = admin_data.get('email', '')
        language = admin_data.get('language', UserLanguage.EN)
        user = User.objects.filter(username=username).first()
        if user:
            user.email = email
            user.role = UserRole.ADMIN
            user.language = language
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.WARNING(f'Admin "{username}" updated.'))
            return user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=UserRole.ADMIN,
            language=language,
            is_staff=True,
            is_superuser=True,
        )
        self.stdout.write(self.style.SUCCESS(f'Created admin: {username}'))
        return user

    def _create_locations(self, locations: list[dict]) -> dict[str, Location]:
        location_map: dict[str, Location] = {}
        for item in locations:
            key = item['key']
            location, created = Location.objects.update_or_create(
                name=item['name'],
                defaults={
                    'location_type': item['location_type'],
                    'sort_order': item.get('sort_order', 0),
                    'is_active': item.get('is_active', True),
                },
            )
            location_map[key] = location
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'{action} location: {location.name}')
        return location_map

    def _create_employees(self, employees: list[dict], location_map: dict[str, Location]) -> None:
        rules_by_code = {rule.code: rule for rule in WorkRule.objects.all()}
        for item in employees:
            nickname = item['nickname']
            location_keys = item.get('location_keys', [])
            rule_codes = item.get('work_rule_codes', [])
            missing_keys = [key for key in location_keys if key not in location_map]
            if missing_keys:
                raise CommandError(
                    f'Employee "{nickname}" references unknown location keys: {missing_keys}.'
                )
            locations = [location_map[key] for key in location_keys]
            work_rules = [rules_by_code[code] for code in rule_codes if code in rules_by_code]
            cycle_start = item.get('cycle_start_date')
            cycle_start_date = date.fromisoformat(cycle_start) if cycle_start else None
            employee_data = {
                'last_name': item['last_name'],
                'first_name': item['first_name'],
                'nickname': nickname,
                'email': item.get('email', ''),
                'phone': item.get('phone', ''),
                'cycle_start_date': cycle_start_date,
                'is_active': item.get('is_active', True),
            }
            existing = Employee.objects.filter(nickname=nickname).first()
            if existing:
                existing.last_name = employee_data['last_name']
                existing.first_name = employee_data['first_name']
                existing.email = employee_data['email']
                existing.phone = employee_data['phone']
                existing.cycle_start_date = cycle_start_date
                existing.is_active = employee_data['is_active']
                existing.save()
                existing.locations.set(locations)
                existing.work_rules.set(work_rules)
                if existing.user:
                    existing.user.set_password(item['password'])
                    existing.user.save()
                self.stdout.write(self.style.WARNING(f'Employee "{nickname}" updated.'))
                continue
            create_employee_with_user(
                employee_data=employee_data,
                password=item['password'],
                locations=locations,
                work_rules=work_rules,
            )
            self.stdout.write(self.style.SUCCESS(f'Created employee: {nickname}'))
