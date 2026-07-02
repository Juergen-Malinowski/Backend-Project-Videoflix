"""Tests for the Videoflix user registration API endpoint."""

import pytest

from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework import status
from rest_framework.test import APIClient

from auth_app.tests.mixins import AuthTestMixin


@pytest.mark.django_db
class TestRegistrationApi(AuthTestMixin):
    """Test POST /api/register/ for user registration behavior."""

    @pytest.fixture(autouse=True)
    def setup_email_backend(self, settings, mailoutbox):
        """Use Django's in-memory email backend for registration email tests."""
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


    def setup_method(self):
        """Prepare API client, endpoint URL and valid registration data."""
        self.client = APIClient()
        self.url = reverse('registration')
        self.valid_registration_data = self.get_registration_data()


    def test_registration_returns_201(self):
        """Test that valid registration data returns HTTP 201 CREATED."""
        response = self.client.post(
            self.url,
            self.valid_registration_data,
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED


    def test_registration_creates_inactive_user(self):
        """Test that a newly registered user is inactive before activation."""
        response = self.client.post(
            self.url,
            self.valid_registration_data,
            format='json',
        )

        user = get_user_model().objects.get(email='user@example.com')

        assert response.status_code == status.HTTP_201_CREATED
        assert user.is_active is False


    def test_registration_hashes_password(self):
        """Test that the password is stored securely and not as plain text."""
        self.client.post(
            self.url,
            self.valid_registration_data,
            format='json',
        )

        user = get_user_model().objects.get(email='user@example.com')

        assert user.check_password('securepassword') is True
        assert user.password != 'securepassword'


    def test_registration_returns_user_data_and_token(self):
        """Test that the response contains user id, email and activation token."""
        response = self.client.post(
            self.url,
            self.valid_registration_data,
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['id'] is not None
        assert response.data['user']['email'] == 'user@example.com'
        assert response.data['token']


    def test_registration_sends_activation_email(self):
        """Test that registration creates one activation email for the user."""
        response = self.client.post(
            self.url,
            self.valid_registration_data,
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ['user@example.com']


    def test_registration_activation_email_contains_activation_url(self):
        """Test that the activation email contains the backend activation URL."""
        response = self.client.post(
            self.url,
            self.valid_registration_data,
            format='json',
        )

        user = get_user_model().objects.get(email='user@example.com')
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        activation_url = f'/api/activate/{uidb64}/{response.data["token"]}/'
        email_body = mail.outbox[0].body

        assert response.status_code == status.HTTP_201_CREATED
        assert activation_url in email_body


    def test_registration_activation_email_contains_frontend_activation_path(self):
        """Test that activation email contains the frontend activation path."""
        response = self.client.post(
            self.url,
            self.valid_registration_data,
            format='json',
        )

        user = get_user_model().objects.get(email='user@example.com')
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        frontend_activation_path = (
            f'/pages/auth/activate.html?uid={uidb64}'
            f'&token={response.data["token"]}'
        )
        email_body = mail.outbox[0].body

        assert response.status_code == status.HTTP_201_CREATED
        assert frontend_activation_path in email_body


    @pytest.mark.parametrize('is_active', [True, False])
    def test_registration_rejects_existing_email(self, is_active):
        """Test that an existing email cannot be registered again."""
        user_model = get_user_model()
        user_model.objects.create_user(
            username='user@example.com',
            email='user@example.com',
            password='existingpassword',
            is_active=is_active,
        )

        response = self.client.post(
            self.url,
            self.valid_registration_data,
            format='json',
        )

        user_count = user_model.objects.filter(
            email='user@example.com',
        ).count()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert user_count == 1


    def test_registration_rejects_existing_username_from_email(self):
        """Test that username conflicts from email mapping are rejected."""
        user_model = get_user_model()
        user_model.objects.create_user(
            username='user@example.com',
            email='other@example.com',
            password='existingpassword',
        )

        response = self.client.post(
            self.url,
            self.valid_registration_data,
            format='json',
        )

        email_exists = user_model.objects.filter(
            email='user@example.com',
        ).exists()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert email_exists is False


    def test_registration_normalizes_email_before_saving(self):
        """Test that email and username are saved in normalized lowercase form."""
        registration_data = self.get_registration_data(
            email='  User@Example.COM  ',
        )

        response = self.client.post(
            self.url,
            registration_data,
            format='json',
        )

        user = get_user_model().objects.get()

        assert response.status_code == status.HTTP_201_CREATED
        assert user.email == 'user@example.com'
        assert user.username == 'user@example.com'
        assert response.data['user']['email'] == 'user@example.com'


    def test_registration_rejects_existing_email_after_normalization(self):
        """Test that normalized duplicate email variants are rejected."""
        self.create_active_user(email='user@example.com')
        registration_data = self.get_registration_data(
            email='  User@Example.COM  ',
        )

        response = self.client.post(
            self.url,
            registration_data,
            format='json',
        )

        user_count = get_user_model().objects.filter(
            email='user@example.com',
        ).count()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert user_count == 1


    def test_registration_rejects_missing_email(self):
        """Test that registration without email returns HTTP 400 BAD REQUEST."""
        registration_data = {
            'password': 'securepassword',
            'confirmed_password': 'securepassword',
        }

        response = self.client.post(
            self.url,
            registration_data,
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert get_user_model().objects.count() == 0


    def test_registration_rejects_missing_password(self):
        """Test that registration without password returns HTTP 400 BAD REQUEST."""
        registration_data = {
            'email': 'user@example.com',
            'confirmed_password': 'securepassword',
        }

        response = self.client.post(
            self.url,
            registration_data,
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert get_user_model().objects.count() == 0


    def test_registration_rejects_missing_confirmed_password(self):
        """Test that registration without password confirmation returns HTTP 400."""
        registration_data = {
            'email': 'user@example.com',
            'password': 'securepassword',
        }

        response = self.client.post(
            self.url,
            registration_data,
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert get_user_model().objects.count() == 0


    def test_registration_rejects_password_mismatch(self):
        """Test that different password values return HTTP 400 BAD REQUEST."""
        registration_data = {
            'email': 'user@example.com',
            'password': 'securepassword',
            'confirmed_password': 'differentpassword',
        }

        response = self.client.post(
            self.url,
            registration_data,
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert get_user_model().objects.count() == 0


    def test_registration_requires_no_authentication(self):
        """Test that unauthenticated users can register successfully."""
        response = self.client.post(
            self.url,
            self.valid_registration_data,
            format='json',
        )

        assert response.status_code == status.HTTP_201_CREATED