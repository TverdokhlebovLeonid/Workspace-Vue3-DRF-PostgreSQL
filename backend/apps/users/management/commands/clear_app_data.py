from django.core.management.base import BaseCommand
from django.db import transaction

from apps.documents.models import Document, DocumentAccess
from apps.schedules.models import Employee, Location, SchedulePeriod, ScheduleShift, WorkRule
from apps.users.models import User


class Command(BaseCommand):
    help = 'Deletes Workspace data: schedule, documents, employees, locations, users.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep-work-rules',
            action='store_true',
            help=('Do not delete the work rules catalog (seed_work_rules will restore if needed).'),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        shift_count = ScheduleShift.objects.count()
        period_count = SchedulePeriod.objects.count()
        document_count = Document.objects.count()
        employee_count = Employee.objects.count()
        location_count = Location.objects.count()
        user_count = User.objects.count()
        ScheduleShift.objects.all().delete()
        SchedulePeriod.objects.all().delete()
        DocumentAccess.objects.all().delete()
        Document.objects.all().delete()
        Employee.objects.all().delete()
        User.objects.all().delete()
        Location.objects.all().delete()
        if not options['keep_work_rules']:
            WorkRule.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(
                f'Cleared: shifts={shift_count}, periods={period_count}, '
                f'documents={document_count}, employees={employee_count}, '
                f'locations={location_count}, users={user_count}.'
            )
        )
