from django.core.management.base import BaseCommand

from apps.schedules.models import RuleKind, WorkRule, WorkRuleCode

DEFAULT_RULES = (
    {
        'code': WorkRuleCode.WORK_2_ON_2,
        'name': '2 days on, 2 days off',
        'kind': RuleKind.CYCLE,
        'description': '2 working days, 2 days off, cycle repeats.',
    },
    {
        'code': WorkRuleCode.WORK_3_ON_2,
        'name': '3 days on, 2 days off',
        'kind': RuleKind.CYCLE,
        'description': '3 working days, 2 days off, cycle repeats.',
    },
    {
        'code': WorkRuleCode.MAX_2_CONSECUTIVE,
        'name': 'No more than 2 consecutive days',
        'kind': RuleKind.CONSTRAINT,
        'description': 'An employee cannot be assigned to the same location three days in a row.',
    },
)


class Command(BaseCommand):
    help = 'Creates or updates default work rules used for schedule generation.'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        for rule_data in DEFAULT_RULES:
            _, created = WorkRule.objects.update_or_create(
                code=rule_data['code'],
                defaults={
                    'name': rule_data['name'],
                    'kind': rule_data['kind'],
                    'description': rule_data['description'],
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
        self.stdout.write(
            self.style.SUCCESS(f'Work rules: {created_count} created, {updated_count} updated.')
        )
