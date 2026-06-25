"""Tests for the Videoflix password confirm API endpoint."""

import pytest

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework import status
from rest_framework.test import APIClient

from auth_app.tests.mixins import AuthTestMixin


@pytest.mark.django_db
class TestPasswordConfirmApi(AuthTestMixin):
    """Test POST /api/password_confirm/<uidb64>/<token>/."""

    def setup_method(self):
        """Prepare API client, active user, URL and valid request data."""

        self.client = APIClient()
        self.user = self.create_active_user(
            email='user@example.com',
            password='oldsecurepassword',
        )
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = f'/api/password_confirm/{self.uidb64}/{self.token}/'
        self.confirm_data = {
            'new_password': 'newsecurepassword',
            'confirm_password': 'newsecurepassword',
        }


    def assert_old_password_is_unchanged(self):
        """Assert that the user's old password is still valid."""

        self.user.refresh_from_db()

        assert self.user.check_password('oldsecurepassword') is True
        assert self.user.check_password('newsecurepassword') is False


    def test_password_confirm_returns_200_with_documented_response(self):
        """Test that valid password confirm returns documented response."""

        response = self.client.post(self.url, self.confirm_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert set(response.data.keys()) == {'detail'}
        assert response.data['detail'] == (
            'Your Password has been successfully reset.'
        )


    def test_password_confirm_changes_user_password(self):
        """Test that password confirm replaces old password with new password."""

        response = self.client.post(self.url, self.confirm_data, format='json')

        self.user.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert self.user.check_password('newsecurepassword') is True
        assert self.user.check_password('oldsecurepassword') is False


    def test_password_confirm_requires_no_authentication(self):
        """Test that unauthenticated users can confirm a password reset."""

        response = self.client.post(self.url, self.confirm_data, format='json')

        assert response.status_code == status.HTTP_200_OK


    def test_password_confirm_rejects_missing_new_password(self):
        """Test that missing new_password returns HTTP 400 BAD REQUEST."""

        data = {'confirm_password': 'newsecurepassword'}

        response = self.client.post(self.url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assert_old_password_is_unchanged()


    def test_password_confirm_rejects_missing_confirm_password(self):
        """Test that missing confirm_password returns HTTP 400 BAD REQUEST."""

        data = {'new_password': 'newsecurepassword'}

        response = self.client.post(self.url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assert_old_password_is_unchanged()


    def test_password_confirm_rejects_mismatched_passwords(self):
        """Test that different password values return HTTP 400 BAD REQUEST."""

        data = {
            'new_password': 'newsecurepassword',
            'confirm_password': 'differentsecurepassword',
        }

        response = self.client.post(self.url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assert_old_password_is_unchanged()


    def test_password_confirm_rejects_invalid_uidb64(self):
        """Test that invalid uidb64 returns HTTP 400 BAD REQUEST."""

        url = f'/api/password_confirm/invalid-uidb64/{self.token}/'

        response = self.client.post(url, self.confirm_data, format='json')

        self.user.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assert_old_password_is_unchanged()


    def test_password_confirm_rejects_unknown_user(self):
        """Test that uidb64 for unknown user returns HTTP 400 BAD REQUEST."""

        unknown_uidb64 = urlsafe_base64_encode(force_bytes(999999))
        url = f'/api/password_confirm/{unknown_uidb64}/{self.token}/'

        response = self.client.post(url, self.confirm_data, format='json')

        self.user.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assert_old_password_is_unchanged()


    def test_password_confirm_rejects_invalid_token(self):
        """Test that invalid reset token returns HTTP 400 BAD REQUEST."""

        url = f'/api/password_confirm/{self.uidb64}/invalid-token/'

        response = self.client.post(url, self.confirm_data, format='json')

        self.user.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assert_old_password_is_unchanged()