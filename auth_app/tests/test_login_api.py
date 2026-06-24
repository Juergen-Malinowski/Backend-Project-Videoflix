"""Tests for the Videoflix login API endpoint."""

import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from auth_app.tests.mixins import AuthTestMixin


@pytest.mark.django_db
class TestLoginApi(AuthTestMixin):
    """Test POST /api/login/ for authentication and token cookie behavior."""

    def setup_method(self):
        """Prepare API client, active user, endpoint URL and login data."""
        self.client = APIClient()
        self.user = self.create_active_user(email='user@example.com')
        self.url = reverse('login')
        self.login_data = self.get_login_data()


    def test_login_returns_200(self):
        """Test that valid login data returns HTTP 200 OK."""
        response = self.client.post(
            self.url,
            self.login_data,
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK


    def test_login_returns_success_detail(self):
        """Test that successful login returns the documented success detail."""
        response = self.client.post(
            self.url,
            self.login_data,
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['detail'] == 'Login successful'


    def test_login_returns_user_data(self):
        """Test that successful login returns the documented user data."""
        response = self.client.post(
            self.url,
            self.login_data,
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['id'] == self.user.id
        assert response.data['user']['username'] == 'user@example.com'


    def test_login_does_not_return_tokens_in_response_body(self):
        """Test that JWT tokens are not exposed in the response body."""
        response = self.client.post(
            self.url,
            self.login_data,
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' not in response.data
        assert 'refresh_token' not in response.data


    def test_login_sets_token_cookies(self):
        """Test that successful login sets non-empty access and refresh token cookies."""
        response = self.client.post(
            self.url,
            self.login_data,
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.cookies
        assert 'refresh_token' in response.cookies
        assert response.cookies['access_token'].value
        assert response.cookies['refresh_token'].value


    def test_login_sets_httponly_token_cookies(self):
        """Test that login token cookies are protected as HttpOnly cookies."""
        response = self.client.post(
            self.url,
            self.login_data,
            format='json',
        )

        access_token = response.cookies['access_token']
        refresh_token = response.cookies['refresh_token']

        assert response.status_code == status.HTTP_200_OK
        assert access_token['httponly'] is True
        assert refresh_token['httponly'] is True


    def test_login_requires_no_authentication(self):
        """Test that unauthenticated users can log in successfully."""
        response = self.client.post(
            self.url,
            self.login_data,
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK


    def test_login_rejects_missing_email(self):
        """Test that login without email returns HTTP 400 BAD REQUEST."""
        login_data = {
            'password': 'securepassword',
        }

        response = self.client.post(
            self.url,
            login_data,
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'access_token' not in response.cookies
        assert 'refresh_token' not in response.cookies


    def test_login_rejects_missing_password(self):
        """Test that login without password returns HTTP 400 BAD REQUEST."""
        login_data = {
            'email': 'user@example.com',
        }

        response = self.client.post(
            self.url,
            login_data,
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'access_token' not in response.cookies
        assert 'refresh_token' not in response.cookies


    def test_login_rejects_unknown_email(self):
        """Test that login with an unknown email returns HTTP 401 UNAUTHORIZED."""
        login_data = self.get_login_data(email='unknown@example.com')

        response = self.client.post(
            self.url,
            login_data,
            format='json',
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'access_token' not in response.cookies
        assert 'refresh_token' not in response.cookies


    def test_login_rejects_wrong_password(self):
        """Test that login with a wrong password returns HTTP 401 UNAUTHORIZED."""
        login_data = self.get_login_data(password='wrongpassword')

        response = self.client.post(
            self.url,
            login_data,
            format='json',
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'access_token' not in response.cookies
        assert 'refresh_token' not in response.cookies


    def test_login_rejects_inactive_user(self):
        """Test that login with an inactive user returns HTTP 401 UNAUTHORIZED."""
        inactive_email = 'inactive@example.com'
        self.create_inactive_user(email=inactive_email)
        login_data = self.get_login_data(email=inactive_email)

        response = self.client.post(
            self.url,
            login_data,
            format='json',
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'access_token' not in response.cookies
        assert 'refresh_token' not in response.cookies


    def test_login_normalizes_email_before_authentication(self):
        """Test that login accepts uppercase and spaced email input."""
        login_data = self.get_login_data(email='  User@Example.COM  ')

        response = self.client.post(
            self.url,
            login_data,
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['username'] == 'user@example.com'
        assert 'access_token' in response.cookies
        assert 'refresh_token' in response.cookies