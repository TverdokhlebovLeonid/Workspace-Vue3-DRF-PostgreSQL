from rest_framework import serializers

from apps.documents.models import Document, DocumentAccess
from apps.schedules.models import Employee


class DocumentAccessEntrySerializer(serializers.Serializer):
    employee_id = serializers.UUIDField()
    granted_at = serializers.DateTimeField()
    granted_by_username = serializers.CharField(allow_null=True)


class DocumentSerializer(serializers.ModelSerializer):
    employee_ids = serializers.SerializerMethodField()
    access_entries = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    can_download = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            'id',
            'title',
            'file_name',
            'created_at',
            'employee_ids',
            'access_entries',
            'can_download',
        )
        read_only_fields = fields

    def get_file_name(self, obj: Document) -> str:
        if not obj.file:
            return ''
        return obj.file.name.split('/')[-1]

    def get_employee_ids(self, obj: Document) -> list:
        if not self.context.get('include_access'):
            return []
        return list(obj.access_entries.values_list('employee_id', flat=True))

    def get_access_entries(self, obj: Document) -> list:
        if not self.context.get('include_access'):
            return []
        return DocumentAccessEntrySerializer(
            [
                {
                    'employee_id': entry.employee_id,
                    'granted_at': entry.granted_at,
                    'granted_by_username': entry.granted_by.username if entry.granted_by else None,
                }
                for entry in obj.access_entries.all()
            ],
            many=True,
        ).data

    def get_can_download(self, obj: Document) -> bool:
        if self.context.get('is_admin'):
            return True
        return bool(self.context.get('can_download_map', {}).get(obj.pk, False))


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('title', 'file')

    def create(self, validated_data):
        request = self.context['request']
        return Document.objects.create(uploaded_by=request.user, **validated_data)


class DocumentAccessUpdateSerializer(serializers.Serializer):
    employee_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=True)

    def validate_employee_ids(self, value):
        existing = set(Employee.objects.filter(pk__in=value).values_list('pk', flat=True))
        missing = set(value) - existing
        if missing:
            raise serializers.ValidationError(
                f'Employees not found: {sorted(str(item) for item in missing)}'
            )
        return value

    def save(self, document: Document) -> Document:
        employee_ids = self.validated_data['employee_ids']
        DocumentAccess.objects.filter(document=document).exclude(
            employee_id__in=employee_ids
        ).delete()
        for employee_id in employee_ids:
            DocumentAccess.objects.get_or_create(
                document=document,
                employee_id=employee_id,
                defaults={'granted_by': self.context['request'].user},
            )
        return document
