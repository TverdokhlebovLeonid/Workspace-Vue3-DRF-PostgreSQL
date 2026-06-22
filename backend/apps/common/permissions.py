from rest_framework.permissions import BasePermission, IsAuthenticated

from apps.users.models import UserRole


class IsAdminRole(BasePermission):
    message = 'Admin role required.'

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user and user.is_authenticated and user.is_active and user.role == UserRole.ADMIN
        )


class IsAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not IsAuthenticated().has_permission(request, view):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return IsAdminRole().has_permission(request, view)
