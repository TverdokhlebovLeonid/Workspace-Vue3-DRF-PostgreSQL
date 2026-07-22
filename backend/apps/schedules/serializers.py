from rest_framework import serializers

from apps.schedules.models import Employee, Location, ScheduleShift, WorkRule
from apps.schedules.services.employee_users import create_employee_with_user, update_employee_user
from apps.users.password_validation import validate_user_password


class LocationSerializer(serializers.ModelSerializer):
    location_type_label = serializers.CharField(source='get_location_type_display', read_only=True)

    class Meta:
        model = Location
        fields = ('id', 'location_type', 'location_type_label', 'name', 'is_active', 'sort_order')


class WorkRuleSerializer(serializers.ModelSerializer):
    kind_label = serializers.CharField(source='get_kind_display', read_only=True)

    class Meta:
        model = WorkRule
        fields = ('id', 'code', 'name', 'kind', 'kind_label', 'description')
        read_only_fields = fields


class EmployeeSerializer(serializers.ModelSerializer):
    location_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Location.objects.filter(is_active=True),
        source='locations',
        required=False,
    )
    work_rule_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=WorkRule.objects.all(), source='work_rules', required=False
    )
    locations = LocationSerializer(many=True, read_only=True)
    work_rules = WorkRuleSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    has_user = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = (
            'id',
            'last_name',
            'first_name',
            'nickname',
            'email',
            'phone',
            'location_ids',
            'work_rule_ids',
            'locations',
            'work_rules',
            'cycle_start_date',
            'is_active',
            'has_user',
            'password',
        )

    def get_has_user(self, obj: Employee) -> bool:
        return bool(obj.user_id)

    def validate_password(self, value: str) -> str:
        if not value:
            return value
        user = self.instance.user if self.instance and self.instance.user_id else None
        return validate_user_password(value, user=user)

    def validate(self, attrs):
        password = attrs.get('password', '')
        if self.instance is None and (not password):
            raise serializers.ValidationError({'password': 'Password is required for login.'})
        return attrs

    def create(self, validated_data):
        locations = validated_data.pop('locations', [])
        work_rules = validated_data.pop('work_rules', [])
        password = validated_data.pop('password')
        return create_employee_with_user(
            employee_data=dict(validated_data),
            password=password,
            locations=locations,
            work_rules=work_rules,
        )

    def update(self, instance, validated_data):
        locations = validated_data.pop('locations', None)
        work_rules = validated_data.pop('work_rules', None)
        password = validated_data.pop('password', None) or None
        employee_fields = {
            'last_name': validated_data.get('last_name', instance.last_name),
            'first_name': validated_data.get('first_name', instance.first_name),
            'nickname': validated_data.get('nickname', instance.nickname),
            'email': validated_data.get('email', instance.email),
            'phone': validated_data.get('phone', instance.phone),
            'cycle_start_date': validated_data.get('cycle_start_date', instance.cycle_start_date),
            'is_active': validated_data.get('is_active', instance.is_active),
        }
        return update_employee_user(
            instance,
            employee_data=employee_fields,
            password=password,
            locations=locations if locations is not None else list(instance.locations.all()),
            work_rules=work_rules if work_rules is not None else list(instance.work_rules.all()),
        )


class ScheduleShiftSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    employee_nickname = serializers.CharField(source='employee.nickname', read_only=True)

    class Meta:
        model = ScheduleShift
        fields = ('id', 'date', 'location', 'location_name', 'employee', 'employee_nickname')


class ScheduleShiftChangeSerializer(serializers.Serializer):
    date = serializers.DateField()
    location_id = serializers.UUIDField()
    employee_id = serializers.UUIDField(allow_null=True, required=False, default=None)


class ScheduleBulkSaveSerializer(serializers.Serializer):
    changes = ScheduleShiftChangeSerializer(many=True, allow_empty=False)
