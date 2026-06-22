from django.urls import path

from apps.users.views import (
    ChangePasswordView,
    HealthView,
    MeView,
    PublicTokenObtainPairView,
    PublicTokenRefreshView,
    UserDetailView,
    UserListCreateView,
)

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('jwt/create/', PublicTokenObtainPairView.as_view(), name='jwt-create'),
    path('jwt/refresh/', PublicTokenRefreshView.as_view(), name='jwt-refresh'),
    path('me/', MeView.as_view(), name='me'),
    path('me/password/', ChangePasswordView.as_view(), name='me-password'),
    path('users/', UserListCreateView.as_view(), name='users'),
    path('users/<uuid:pk>/', UserDetailView.as_view(), name='user-detail'),
]
