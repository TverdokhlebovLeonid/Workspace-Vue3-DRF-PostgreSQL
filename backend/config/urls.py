from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/schedules/', include('apps.schedules.urls')),
    path('api/documents/', include('apps.documents.urls')),
]
if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def _api_docs_urlpatterns():
    from django.conf import settings

    if not getattr(settings, 'ENABLE_API_DOCS', False):
        return []
    return [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path(
            'api/schema/swagger-ui/',
            SpectacularSwaggerView.as_view(url_name='schema'),
            name='swagger-ui',
        ),
    ]


urlpatterns += _api_docs_urlpatterns()
