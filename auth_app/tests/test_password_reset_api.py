"""Tests for the Videoflix password reset API endpoint."""

import pytest

from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework import status
from rest_framework.test import APIClient

from auth_app.tests.mixins import AuthTestMixin


@pytest.mark.django_db
class TestPasswordResetApi(AuthTestMixin):
    """Test POST /api/password_reset/ for password reset email requests."""

    @pytest.fixture(autouse=True)
    def setup_email_backend(self, settings, mailoutbox):
        """Use Django's in-memory email backend for password reset tests."""

        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


    def setup_method(self):
        """Prepare API client, active user, endpoint URL and request data."""

        self.client = APIClient()
        self.user = self.create_active_user(email='user@example.com')
        self.url = reverse('password-reset')
        self.reset_data = {'email': 'user@example.com'}


    def test_password_reset_returns_200_with_documented_response(self):
        """Test that existing email returns HTTP 200 and documented response."""

        response = self.client.post(self.url, self.reset_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert set(response.data.keys()) == {'detail'}
        assert response.data['detail'] == (
            'An email has been sent to reset your password.'
        )


    def test_password_reset_sends_email_with_password_confirm_url(self):
        """Test that password reset sends one email with password confirm URL."""

        response = self.client.post(self.url, self.reset_data, format='json')

        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        reset_url = f'/api/password_confirm/{uidb64}/{token}/'

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ['user@example.com']
        assert reset_url in mail.outbox[0].body


    def test_password_reset_email_contains_frontend_confirm_path(self):
        """Test that reset email contains the frontend password confirm path."""

        response = self.client.post(self.url, self.reset_data, format='json')

        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        frontend_confirm_path = (
            f'/pages/auth/confirm_password.html?uid={uidb64}'
            f'&token={token}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert frontend_confirm_path in mail.outbox[0].body


    def test_password_reset_requires_no_authentication(self):
        """Test that unauthenticated users can request password reset email."""

        response = self.client.post(self.url, self.reset_data, format='json')

        assert response.status_code == status.HTTP_200_OK


    def test_password_reset_rejects_missing_email(self):
        """Test that missing email returns HTTP 400 BAD REQUEST."""

        response = self.client.post(self.url, {}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_password_reset_returns_200_for_unknown_email_without_sending_email(self):
        """Test that unknown email gets neutral response without reset email."""

        data = {'email': 'unknown@example.com'}

        response = self.client.post(self.url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['detail'] == (
            'An email has been sent to reset your password.'
        )
        assert len(mail.outbox) == 0