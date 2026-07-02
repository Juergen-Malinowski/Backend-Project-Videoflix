"""Utility functions for the Videoflix authentication API."""

from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


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