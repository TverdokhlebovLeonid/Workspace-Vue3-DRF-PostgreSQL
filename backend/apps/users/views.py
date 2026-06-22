from django.db import connection
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.common.permissions import IsAdminRole
from apps.users.models import User, UserRole
from apps.users.serializers import (
    ChangePasswordSerializer,
    UserCreateSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
)


class AuthRateThrottle(AnonRateThrottle):
    scope = 'auth'


class PublicTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
    throttle_classes = (AuthRateThrottle,)


class PublicTokenRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
    throttle_classes = (AuthRateThrottle,)


@extend_schema(responses=UserSerializer)
class MeView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get', 'patch', 'head', 'options')

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UserProfileUpdateSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(UserSerializer(instance).data)


@extend_schema(request=ChangePasswordSerializer, responses={200: dict})
class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password'])
        return Response({'detail': 'Password updated.'})


@extend_schema(responses=UserSerializer(many=True))
class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAdminRole,)
    queryset = UserSerializer.Meta.model.objects.all().order_by('username')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


@extend_schema(responses={204: None})
class UserDetailView(generics.DestroyAPIView):
    permission_classes = (IsAdminRole,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_destroy(self, instance):
        if instance.pk == self.request.user.pk:
            raise ValidationError('Cannot delete your own account.')
        if (
            instance.role == UserRole.ADMIN
            and User.objects.filter(role=UserRole.ADMIN).count() <= 1
        ):
            raise ValidationError('Cannot delete the last admin.')
        super().perform_destroy(instance)


class HealthView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    @extend_schema(
        responses={
            200: {'type': 'object', 'properties': {'status': {'type': 'string'}}},
            503: {'type': 'object', 'properties': {'status': {'type': 'string'}}},
        }
    )
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
        except Exception:
            return Response(
                {'status': 'error', 'database': 'unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({'status': 'ok', 'database': 'ok'}, status=status.HTTP_200_OK)
