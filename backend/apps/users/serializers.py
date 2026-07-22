from rest_framework import serializers

from apps.users.models import User, UserLanguage, UserRole
from apps.users.password_validation import validate_user_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'language')
        read_only_fields = fields


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('language',)

    def validate_language(self, value: str) -> str:
        if value not in UserLanguage.values:
            raise serializers.ValidationError('Invalid language.')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value: str) -> str:
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Incorrect current password.')
        return value

    def validate_new_password(self, value: str) -> str:
        return validate_user_password(value, user=self.context['request'].user)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')

    def validate_role(self, value: str) -> str:
        if value not in UserRole.values:
            raise serializers.ValidationError('Invalid role.')
        return value

    def validate_password(self, value: str) -> str:
        return validate_user_password(value)

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.get('role', UserRole.USER)
        user = User(**validated_data)
        user.set_password(password)
        user.is_staff = role == UserRole.ADMIN
        user.save()
        return user
