"""Reusable test helpers for Videoflix authentication API tests."""

from django.contrib.auth import get_user_model


class AuthTestMixin:
    """Provide reusable helpers for authentication API tests."""

    def get_registration_data(self, email='user@example.com'):
        """Return valid request data for the registration endpoint."""
        return {
            'email': email,
            'password': 'securepassword',
            'confirmed_password': 'securepassword',
        }


    def create_active_user(self, email='user@example.com', password='securepassword'):
        """Create and return an active Django user for authentication tests."""
        user_model = get_user_model()
        return user_model.objects.create_user(
            username=email,
            email=email,
            password=password,
            is_active=True,
        )


    def create_inactive_user(self, email='user@example.com', password='securepassword'):
        """Create and return an inactive Django user for activation tests."""
        user_model = get_user_model()
        return user_model.objects.create_user(
            username=email,
            email=email,
            password=password,
            is_active=False,
        )


    def get_login_data(self, email='user@example.com', password='securepassword'):
        """Return valid request data for the login endpoint."""
        return {
            'email': email,
            'password': password,
        }