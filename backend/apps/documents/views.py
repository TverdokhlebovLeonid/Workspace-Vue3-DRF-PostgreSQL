import mimetypes
import os

from django.http import FileResponse, Http404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsAdminRole
from apps.documents.models import Document, DocumentAccess
from apps.documents.serializers import (
    DocumentAccessUpdateSerializer,
    DocumentSerializer,
    DocumentUploadSerializer,
)
from apps.users.models import UserRole


class DocumentListCreateView(generics.ListCreateAPIView):
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminRole()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentUploadSerializer
        return DocumentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.ADMIN:
            return Document.objects.all().prefetch_related('access_entries__granted_by')
        employee = getattr(user, 'employee_profile', None)
        if not employee:
            return Document.objects.none()
        return (
            Document.objects.filter(access_entries__employee=employee)
            .distinct()
            .prefetch_related('access_entries')
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        is_admin = user.role == UserRole.ADMIN
        context['include_access'] = is_admin
        context['is_admin'] = is_admin
        can_download_map = {}
        if not is_admin:
            employee = getattr(user, 'employee_profile', None)
            if employee:
                for doc_id in DocumentAccess.objects.filter(employee=employee).values_list(
                    'document_id', flat=True
                ):
                    can_download_map[doc_id] = True
        context['can_download_map'] = can_download_map
        return context


class DocumentDetailView(generics.DestroyAPIView):
    permission_classes = (IsAdminRole,)
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class DocumentAccessUpdateView(APIView):
    permission_classes = (IsAdminRole,)

    @extend_schema(request=DocumentAccessUpdateSerializer, responses=DocumentSerializer)
    def patch(self, request, pk):
        try:
            document = Document.objects.prefetch_related('access_entries__granted_by').get(pk=pk)
        except Document.DoesNotExist as exc:
            raise Http404 from exc
        serializer = DocumentAccessUpdateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(document=document)
        document = Document.objects.prefetch_related('access_entries__granted_by').get(
            pk=document.pk
        )
        output = DocumentSerializer(
            document,
            context={
                'request': request,
                'include_access': True,
                'is_admin': True,
            },
        )
        return Response(output.data)


class DocumentDownloadView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist as exc:
            raise Http404 from exc
        user = request.user
        if user.role != UserRole.ADMIN:
            employee = getattr(user, 'employee_profile', None)
            if (
                not employee
                or not DocumentAccess.objects.filter(document=document, employee=employee).exists()
            ):
                return Response({'detail': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
        if not document.file:
            raise Http404
        content_type, _ = mimetypes.guess_type(document.file.name)
        filename = os.path.basename(document.file.name)
        return FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=filename,
            content_type=content_type or 'application/octet-stream',
        )
