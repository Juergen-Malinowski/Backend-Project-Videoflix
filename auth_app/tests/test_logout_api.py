"""Tests for the Videoflix logout API endpoint."""

import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.tests.mixins import AuthTestMixin


@pytest.mark.django_db
class TestLogoutApi(AuthTestMixin):
    """Test POST /api/logout/ for cookie cleanup and refresh token blacklisting."""

    def setup_method(self):
        """Prepare API client, active user, endpoint URL and refresh token."""
        self.client = APIClient()
        self.user = self.create_active_user(email='user@example.com')
        self.url = reverse('logout')
        self.refresh_token = RefreshToken.for_user(self.user)


    def test_logout_returns_200_with_refresh_token_cookie(self):
        """Test that logout with a refresh token cookie returns HTTP 200 OK."""
        self.client.cookies['refresh_token'] = str(self.refresh_token)

        response = self.client.post(self.url, {}, format='json')

        assert response.status_code == status.HTTP_200_OK


    def test_logout_returns_success_detail(self):
        """Test that successful logout returns the documented detail message."""
        self.client.cookies['refresh_token'] = str(self.refresh_token)

        response = self.client.post(self.url, {}, format='json')

        expected_detail = (
            'Logout successful! All tokens will be deleted. '
            'Refresh token is now invalid.'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['detail'] == expected_detail


    def test_logout_deletes_auth_token_cookies(self):
        """Test that logout sends expired access and refresh token cookies."""
        self.client.cookies['access_token'] = 'existing-access-token'
        self.client.cookies['refresh_token'] = str(self.refresh_token)

        response = self.client.post(self.url, {}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.cookies
        assert 'refresh_token' in response.cookies
        assert response.cookies['access_token'].value == ''
        assert response.cookies['refresh_token'].value == ''


    def test_logout_rejects_missing_refresh_token_cookie(self):
        """Test that logout without refresh token cookie returns HTTP 400."""

        assert 'refresh_token' not in self.client.cookies

        response = self.client.post(self.url, {}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_logout_without_refresh_token_does_not_blacklist_token(self):
        """Test that missing refresh token does not create blacklist entries."""
        response = self.client.post(self.url, {}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert BlacklistedToken.objects.count() == 0


    def test_logout_blacklists_refresh_token(self):
        """Test that logout adds the refresh token to the token blacklist."""
        self.client.cookies['refresh_token'] = str(self.refresh_token)

        response = self.client.post(self.url, {}, format='json')

        token_is_blacklisted = BlacklistedToken.objects.filter(
            token__jti=self.refresh_token['jti'],
        ).exists()

        assert response.status_code == status.HTTP_200_OK
        assert token_is_blacklisted is True