"""Tests for the Videoflix token refresh API endpoint."""

import pytest

from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.tests.mixins import AuthTestMixin


@pytest.mark.django_db
class TestTokenRefreshApi(AuthTestMixin):
    """Test POST /api/token/refresh/ for access token renewal."""

    def setup_method(self):
        """Prepare API client, active user, endpoint URL and refresh token."""

        self.client = APIClient()
        self.user = self.create_active_user(email='user@example.com')
        self.url = reverse('token-refresh')
        self.refresh_token = RefreshToken.for_user(self.user)


    def test_token_refresh_returns_200_with_valid_refresh_token(self):
        """Test that a valid refresh token cookie returns HTTP 200 OK."""

        self.client.cookies['refresh_token'] = str(self.refresh_token)

        response = self.client.post(self.url, {}, format='json')

        assert response.status_code == status.HTTP_200_OK


    def test_token_refresh_returns_documented_response(self):
        """Test that token refresh returns the documented response structure."""

        self.client.cookies['refresh_token'] = str(self.refresh_token)

        response = self.client.post(self.url, {}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert set(response.data.keys()) == {'detail', 'access'}
        assert response.data['detail'] == 'Token refreshed'
        assert isinstance(response.data['access'], str)
        assert response.data['access']


    def test_token_refresh_sets_access_token_cookie(self):
        """Test that successful token refresh sets a non-empty access cookie."""

        self.client.cookies['refresh_token'] = str(self.refresh_token)

        response = self.client.post(self.url, {}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.cookies
        assert response.cookies['access_token'].value


    def test_token_refresh_sets_httponly_access_token_cookie(self):
        """Test that the refreshed access token cookie is HttpOnly."""

        self.client.cookies['refresh_token'] = str(self.refresh_token)

        response = self.client.post(self.url, {}, format='json')

        access_token = response.cookies['access_token']

        assert response.status_code == status.HTTP_200_OK
        assert access_token['httponly'] is True


    def test_token_refresh_sets_access_token_cookie_max_age_from_settings(self):
        """Test that refreshed access cookie uses the configured JWT lifetime."""

        self.client.cookies['refresh_token'] = str(self.refresh_token)

        response = self.client.post(self.url, {}, format='json')

        access_token = response.cookies['access_token']
        expected_access_max_age = int(
            settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
        )

        assert response.status_code == status.HTTP_200_OK
        assert int(access_token['max-age']) == expected_access_max_age


    def test_token_refresh_rejects_missing_refresh_token_cookie(self):
        """Test that missing refresh token cookie returns HTTP 400."""

        assert 'refresh_token' not in self.client.cookies

        response = self.client.post(self.url, {}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_token_refresh_rejects_invalid_refresh_token(self):
        """Test that an invalid refresh token cookie returns HTTP 401."""

        self.client.cookies['refresh_token'] = 'invalid-refresh-token'

        response = self.client.post(self.url, {}, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_token_refresh_without_refresh_token_sets_no_access_cookie(self):
        """Test that missing refresh token does not set an access cookie."""

        assert 'refresh_token' not in self.client.cookies

        response = self.client.post(self.url, {}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'access_token' not in response.cookies


    def test_token_refresh_with_invalid_token_sets_no_access_cookie(self):
        """Test that invalid refresh token does not set an access cookie."""

        self.client.cookies['refresh_token'] = 'invalid-refresh-token'

        response = self.client.post(self.url, {}, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'access_token' not in response.cookies