"""Serializers for the Videoflix authentication API."""

from django.contrib.auth import authenticate, get_user_model

from rest_framework import serializers, status
from rest_framework.exceptions import APIException


class LoginFailed(APIException):
    """Represent failed login authentication with HTTP 401."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Please check your input and try again.'
    default_code = 'authentication_failed'


class RegistrationSerializer(serializers.Serializer):
    """Validate registration data and create inactive users."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate registration data before user creation."""

        email = attrs['email'].strip().lower()

        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError(
                'Please check your input and try again.',
            )

        self._validate_unique_user(email)
        attrs['email'] = email
        return attrs


    def _validate_unique_user(self, email):
        """Raise a validation error if email or username already exists."""

        user_model = get_user_model()

        if user_model.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Please check your input and try again.',
            )

        if user_model.objects.filter(username=email).exists():
            raise serializers.ValidationError(
                'Please check your input and try again.',
            )


    def create(self, validated_data):
        """Create an inactive user with email as username."""

        email = validated_data['email']
        password = validated_data['password']

        return get_user_model().objects.create_user(
            username=email,
            email=email,
            password=password,
            is_active=False,
        )


class LoginSerializer(serializers.Serializer):
    """Validate login data and authenticate active users."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate login credentials and return authenticated user."""

        email = attrs['email'].strip().lower()
        user = authenticate(
            username=email,
            password=attrs['password'],
        )

        if user is None or not user.is_active:
            raise LoginFailed()

        attrs['email'] = email
        attrs['user'] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """Validate password reset request data."""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Return a normalized password reset email address."""

        return value.strip().lower()


class PasswordConfirmSerializer(serializers.Serializer):
    """Validate password confirmation data."""

    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate that both password fields match."""

        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                'Please check your input and try again.',
            )

        return attrs