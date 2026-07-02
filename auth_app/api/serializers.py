"""Serializers for the Videoflix authentication API."""

from django.contrib.auth import get_user_model

from rest_framework import serializers


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


