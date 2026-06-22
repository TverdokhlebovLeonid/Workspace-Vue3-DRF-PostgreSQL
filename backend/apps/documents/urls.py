from django.urls import path

from apps.documents.views import (
    DocumentAccessUpdateView,
    DocumentDetailView,
    DocumentDownloadView,
    DocumentListCreateView,
)

urlpatterns = [
    path('', DocumentListCreateView.as_view(), name='documents-list'),
    path('<uuid:pk>/', DocumentDetailView.as_view(), name='documents-detail'),
    path('<uuid:pk>/access/', DocumentAccessUpdateView.as_view(), name='documents-access'),
    path('<uuid:pk>/download/', DocumentDownloadView.as_view(), name='documents-download'),
]
