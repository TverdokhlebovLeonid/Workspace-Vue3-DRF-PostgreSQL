from django.contrib import admin

from apps.documents.models import Document, DocumentAccess


class DocumentAccessInline(admin.TabularInline):
    model = DocumentAccess
    extra = 0


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'created_at')
    inlines = (DocumentAccessInline,)


@admin.register(DocumentAccess)
class DocumentAccessAdmin(admin.ModelAdmin):
    list_display = ('document', 'employee', 'granted_at', 'granted_by')
