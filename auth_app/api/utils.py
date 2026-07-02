"""Utility functions for the Videoflix authentication API."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


def build_activation_url(user, token):
    """Build the backend account activation URL for a user."""

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    return f'/api/activate/{uidb64}/{token}/'


def build_frontend_activation_path(user, token):
    """Build the frontend account activation path for a user."""

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    return f'/pages/auth/activate.html?uid={uidb64}&token={token}'


def build_activation_email_message(user, token):
    """Build the plain text activation email message."""

    frontend_path = build_frontend_activation_path(user, token)
    activation_url = build_activation_url(user, token)

    return (
        'Welcome to Videoflix.\n\n'
        'Please activate your account using this link:\n'
        f'{frontend_path}\n\n'
        'Backend activation endpoint:\n'
        f'{activation_url}\n\n'
        'If you did not create this account, you can ignore this email.'
    )


def send_activation_email(user, token):
    """Send an account activation email to a newly registered user."""

    message = build_activation_email_message(user, token)

    send_mail(
        subject='Activate your Videoflix account',
        message=message,
        from_email=None,
        recipient_list=[user.email],
    )


def get_user_from_uidb64(uidb64):
    """Return a user for a base64 encoded user id."""

    user_model = get_user_model()

    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        return user_model.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        return None


def set_auth_cookies(response, access_token, refresh_token):
    """Set HttpOnly JWT authentication cookies on a response."""

    response.set_cookie(
        key='access_token',
        value=str(access_token),
        httponly=True,
        samesite='Lax',
        max_age=int(timedelta(minutes=5).total_seconds()),
    )
    response.set_cookie(
        key='refresh_token',
        value=str(refresh_token),
        httponly=True,
        samesite='Lax',
        max_age=int(timedelta(days=1).total_seconds()),
    )