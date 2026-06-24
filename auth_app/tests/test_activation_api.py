"""Tests for the Videoflix account activation API endpoint."""

import pytest

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework import status
from rest_framework.test import APIClient

from auth_app.tests.mixins import AuthTestMixin


@pytest.mark.django_db
class TestAccountActivationApi(AuthTestMixin):
    """Test GET /api/activate/<uidb64>/<token>/ for account activation."""

    def setup_method(self):
        """Prepare API client, inactive user and valid activation URL."""
        self.client = APIClient()
        self.user = self.create_inactive_user(email='user@example.com')
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = f'/api/activate/{self.uidb64}/{self.token}/'


    def test_activation_returns_200_without_authentication(self):
        """Test that unauthenticated users can activate an account."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK


    def test_activation_returns_success_message(self):
        """Test that successful activation returns the documented message."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Account successfully activated.'


    def test_activation_sets_user_active(self):
        """Test that a valid activation request activates the user account."""
        response = self.client.get(self.url)

        self.user.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert self.user.is_active is True


    def test_activation_rejects_invalid_uidb64(self):
        """Test that an invalid uidb64 returns HTTP 400 BAD REQUEST."""
        url = f'/api/activate/invalid-uidb64/{self.token}/'

        response = self.client.get(url)

        self.user.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert self.user.is_active is False


    def test_activation_rejects_unknown_user(self):
        """Test that uidb64 for a non-existing user returns HTTP 400."""
        unknown_uidb64 = urlsafe_base64_encode(force_bytes(999999))
        url = f'/api/activate/{unknown_uidb64}/{self.token}/'

        response = self.client.get(url)

        self.user.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert self.user.is_active is False


    def test_activation_rejects_invalid_token(self):
        """Test that an invalid activation token returns HTTP 400."""
        url = f'/api/activate/{self.uidb64}/invalid-token/'

        response = self.client.get(url)

        self.user.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert self.user.is_active is False